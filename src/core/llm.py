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
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from settings import settings

# Initialize the appropriate LLM based on configuration
# https://python.langchain.com/docs/introduction/
if settings.llm_provider.lower() == "openai":
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    default_llm = ChatOpenAI(temperature=0.7, model=settings.llm_model)

elif settings.llm_provider.lower() == "azure":
    os.environ["AZURE_OPENAI_API_KEY"] = settings.azure_openai_api_key
    os.environ["AZURE_OPENAI_API_ENDPOINT"] = settings.azure_openai_api_endpoint
    os.environ["AZURE_OPENAI_API_VERSION"] = settings.azure_openai_api_version
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = settings.azure_openai_deployment_name
    default_llm = model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_API_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        temperature=0.7,
        model=settings.llm_model
    )
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
        self._memory = {}


    # def set_configuration(self, your_role: str, document_purpose: str):
    #     """
    #     Update the agent's configuration.
    #     """
    #     self.role = your_role
    #     self.document_purpose = document_purpose
    #     self.lang = lang



    def remember(self, AI_task: str, section_id: str, document_filename: str, text: str = False):
        """
        Remember the AI task for a specific section of the document.
        """
        if document_filename not in self._memory:
            self._memory[document_filename] = {}
        if section_id not in self._memory[document_filename]:
            self._memory[document_filename][section_id] = {}
        if AI_task not in self._memory[document_filename][section_id]:
            self._memory[document_filename][section_id][AI_task] = False
        
        if text:
            self._memory[document_filename][section_id][AI_task] = text
            
        return self._memory[document_filename][section_id][AI_task]

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



    def analyse_section_in_context(self, document: str, section: str) -> str:
        # Analyze the section in the context of the whole document
        prompt = """
You are a smart reviewer with a deep understanding of the document's purpose and structure. Also you were designated with the role of "{role}" in the review of this document, written in "{lang}". The document has the declared purpose of "{purpose}".

For section written below, you will evaluate the following criteria:

- **Extension**: Is the section comparable in length to other sections?
- **Clarity**: Is the section clear and easy to understand?
- **Consistency**: Is the section consistent with the rest of the document?
- **Correctness**: Is the section correct and free of errors, does it has all the needed information expected for this kind of document?
- **Style and tone**: Is the section in the correct style and tone for the document?

For each criteria, if it is ok just write "Ok", otherwise provide a one line with problems or improvements needed.

==== Document ====
{document}
==== EOF Document ====

==== Section to analyze ====
{section}
==== EOF Section ====

The evaluation is:
"""
        prompt_template = PromptTemplate(
            input_variables=["document", "section", "lang", "role", "purpose"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(document=document, section=section, lang=self.lang, role=self.role, purpose=self.purpose)
        return result


    def suggest_section_content(self, document: str, section: str) -> str:
        prompt = """
Your role in the review of this document is: {role} in native {lang} language.
Document purpose: {purpose}

You will be provided with a specific section to rewrite in the context of a whole document in process of creation. For this,

1. Asses the content of the section in extension, tone, and style.
2. Rewrite the content of the section to match the style of the whole document, infer from the whole document if needed.
3. Add new content if needed to improve the section. If you don't have the information, insert [placeholders] to guide the author.
4. Keep the same style and tone in the corrections, ignore literals in case of programming examples.
5. Do not add new sections, just improve the content of the section.

==== Document ====
{document}
==== EOF Document ====

==== Section to rewrite ====
{section}
==== EOF Section ====

The suggested new section content is:
"""
        prompt_template = PromptTemplate(
            input_variables=["document", "section", "lang", "role", "purpose"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(document=document, section=section, lang=self.lang, role=self.role, purpose=self.purpose)
        return result
    
    

    def review_grammar(self ,content: str) -> dict:
        prompt = """
Your role in the review of this document is: Grammar and spelling reviewer in native {lang} language.
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
    

    def infer_markdown_from_pdf(self, pdf_content: str) -> str:
        prompt = """
You are a {role} with the purpose of: "{purpose}".
The document must be written in language: {lang}

This markdown is a poorly translated PDF. Your mission is to do your best to transform the text in correct markdown which also has sense, inferred from the topic of the document. Take special care in title ordering, enumerations, lists, etc. Also, the document could contain spelling errors and pagination, take care of it to provide the cleanest possible markdown.

========================
{pdf_content}
========================
"""
        prompt_template = PromptTemplate(
            input_variables=["role", "purpose", "lang", "pdf_content"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        result = chain.run(role=self.role, purpose=self.purpose, lang=self.lang, pdf_content=pdf_content)
        return result
    
llm = LLMDocumentAgent(
    role="Expert in the topic of the document",
    purpose="Inferred from the document",
    lang="Inferred from the document"
)
