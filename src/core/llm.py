"""
llm.py

A structured document analysis agent using LangChain.
This file imports configuration from settings.py to load credentials for OpenAI or Gemini.
It supports overall document analysis, section-specific analysis, and hint generation.
All inputs are assumed to be in markdown format.
"""

import re
import os
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from settings import settings

# Initialize the appropriate LLM based on configuration
# https://python.langchain.com/docs/introduction/
if settings.llm_provider.lower() == "openai":
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    default_llm = ChatOpenAI(temperature=0.7, model=settings.llm_model)
    
else:
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

import json
import re


def recover_json(input_string):
    # Attempt to extract JSON content (either array or object)
    match = re.search(r'(\[.*\]|\{.*\})', input_string, re.DOTALL)
    
    if match:
        json_str = match.group(1)  # Extract matched JSON content
        try:
            return json.loads(json_str)  # Parse JSON
        except json.JSONDecodeError:
            return None  # Invalid JSON
    return None  # No valid JSON found





class LLMDocumentAgent:
    def __init__(self, role: str="", purpose: str="", lang: str="", llm=None):
        """
        Initialize the document analysis agent.

        :param your_role: The role assigned to the agent (e.g., "Document Analysis Expert").
        :param document_purpose: The intended purpose of analyzing the document.
        :param llm: Optional LLM instance; if not provided, a default is used based on settings.
        """
        self.role = role
        self.purpose = purpose
        self.lang = lang
        self.llm = llm if llm is not None else default_llm


    # def set_configuration(self, your_role: str, document_purpose: str):
    #     """
    #     Update the agent's configuration.
    #     """
    #     self.role = your_role
    #     self.document_purpose = document_purpose
    #     self.lang = lang


    def analyze_overall(self, markdown_text: str) -> str:
        """
        Perform an overall analysis of the complete markdown document.
        
        :param markdown_text: The entire document in markdown.
        :return: Analysis result as a string.
        """
        prompt = f"""
Your role is: {self.role}
Document purpose: {self.purpose}

Perform an overall analysis of the following markdown document:
{markdown_text}
"""
        prompt_template = PromptTemplate(
            input_variables=["document"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(document=markdown_text)
        return result

    def analyze_section(self, markdown_text: str, section_title: str) -> str:
        """
        Extract a section by its markdown heading and perform a detailed analysis.
        
        :param markdown_text: The full markdown document.
        :param section_title: The title of the section to analyze (e.g., "Usage").
        :return: Analysis result for the section, or an error message if not found.
        """
        # Extract the section using regex (captures until the next markdown heading)
        pattern = rf"(#{1,6}\s+{re.escape(section_title)}.*?)(?=\n#|\Z)"
        match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1).strip()
        else:
            return f"Section '{section_title}' not found in the document."

        prompt = f"""
Your role is: {self.role}
Document purpose: {self.purpose}

Perform a detailed analysis on the following section extracted from a markdown document:
Section Title: {section_title}

Section Content:
{section_text}
"""
        prompt_template = PromptTemplate(
            input_variables=["section"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(section=section_text)
        return result



    def review_grammar(self ,content: str) -> dict:
        prompt = """
Your role in the review of this document is: Grammar and sintax reviewer in native {lang} language.
Document purpose: {purpose}

You will be provided with the content of a document in process of creation. For this,

1. Asses grammar, spelling and sintax correctness in {lang}
2. Verify titles, content, lists, etc.
3. Create a list of up to 10 problems, keep the critical ones, and ommit merely style improvements.
4. Select excerpts with the example of the problems. Select the minimum context to be understable, around twenty words. 
5. Keep the same style and tone in the corrections, ignore literals in case of programming examples. 
6. Consider that some documents could have no problems at all, if nothing is found don't hallucinate please. If no important problems are found, return an empty list []
7. Look for incomplete phrases, incoherent phrases, mispelled words, non-sense phrases. Propose a correction.
8. Delete the content is a valid suggestion and should be proposed as an empty string
9. Order the results based on criticity
10. If there are text in language different than {lang}, translate it to the main document language.

The excerpts in field 'original' must be identical to original document: keep the case, symbols, new lines and existing markdown to be able to do search and replace. The result must be written in correct json format, escaped literals, etc. BAD_CONTENT is equal than CORRECTED_CONTENT.  

    'section': SECTION_NAME (inferred from the title),
    'original: BAD_CONTENT,
    'corrected': CORRECTED_CONTENT

The content to be analyzed is below:
========================
{content}
========================

The generated JSON is:
"""

        prompt_template = PromptTemplate(
            input_variables=["role", "purpose", "lang", "content"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        # result = chain.run(section=section_text)
        result = chain.run(role=self.role, purpose=self.purpose, lang=self.lang, content=content)
        return recover_json(result)
        

    def generate_hint(self, markdown_text: str) -> str:
        """
        Generate a hint based on the overall analysis of the document.
        
        :param markdown_text: The markdown document to analyze.
        :return: A generated hint as a string.
        """
        overall_hint = self.analyze_overall(markdown_text)
        return overall_hint
    
    
    def extract_content_assessment(self, document_content: str) -> dict:
        prompt = """
Based on your role in the review of this document: "{role}"
And the partial declared purpose of "{purpose}"

You will be provided a document in preparation. 

1. Infer what type of document it is, inferring possible audience and distribution
2. Infer the general purpose of this kind of documents
3. Write a short paragraph on what the content of a document of this type should have
4. Based on 1. and 2. and in my role of {role}, define 5 criterias to evaluate its content. Check also if text seems to be incomplete or missing.
5. For each criteria, write a paragraph with one of [👌 achieved, 😐 partially achieved, 🔧 to be improved], followed by the assessment of the criteria
6. For each criteria, write a paragraph with recommendations, howver if the assessment is overall positive then a "nothing to change" is a valid answer too.

The result must be written in JSON with exactly these text fields:

- purpose: str
- type_of_document: str
- expected_content: str
- criteria: list of five str
- assessment: list of five str
- recommendations: list of five str

Return the results in language = {lang}

The document to be analyzed is below:
========================
{content}
========================

The generated JSON is:
"""

        prompt_template = PromptTemplate(
            input_variables=["role", "purpose", "lang", "content"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(role=self.role, purpose=self.purpose, lang=self.lang, content=document_content)
        return recover_json(result)    
        # return result
    
    
    def create_content(self, title: str) -> str:
        prompt = """
You are a {role} with the purpose: "{purpose}".
The document must be written in language: {lang}
You are asked to create the barebones of a markdown document with title: "{title}". Infer the best style of writting and fill with some few initial content, leaving placeholders for the user to fill in the rest.
"""
        prompt_template = PromptTemplate(
            input_variables=["role", "purpose", "title", "lang"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(role=self.role, purpose=self.purpose, title=title, lang=self.lang)
        print(result)
        return result
    
    
llm = LLMDocumentAgent(
    role="Expert in the topic of the document",
    purpose="Inferred from the document",
    lang="Inferred from the document"
)
