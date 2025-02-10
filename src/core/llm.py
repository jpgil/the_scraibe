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
    default_llm = ChatOpenAI(temperature=1, model=settings.llm_model)
    
else:
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

import json
import re


def recover_json(input_string):
    # Try to extract content between square brackets []
    match = re.search(r'\[(.*)\]', input_string, re.DOTALL)
    if match:
        json_str = match.group(0)  # Get the whole content including the brackets
        try:
            # Parse the extracted string to JSON
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("Invalid JSON format after extraction.")
            return None
    else:
        print("No valid JSON array found.")
        return None




class LLMDocumentAgent:
    def __init__(self, user_role: str="", purpose: str="", lang: str="", llm=None):
        """
        Initialize the document analysis agent.

        :param your_role: The role assigned to the agent (e.g., "Document Analysis Expert").
        :param document_purpose: The intended purpose of analyzing the document.
        :param llm: Optional LLM instance; if not provided, a default is used based on settings.
        """
        self.my_role = user_role
        self.purpose = purpose
        self.lang = lang
        self.llm = llm if llm is not None else default_llm


    # def set_configuration(self, your_role: str, document_purpose: str):
    #     """
    #     Update the agent's configuration.
    #     """
    #     self.my_role = your_role
    #     self.document_purpose = document_purpose
    #     self.lang = lang


    def analyze_overall(self, markdown_text: str) -> str:
        """
        Perform an overall analysis of the complete markdown document.
        
        :param markdown_text: The entire document in markdown.
        :return: Analysis result as a string.
        """
        prompt = f"""
Your role is: {self.my_role}
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
Your role is: {self.my_role}
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



# Perform a a grammar and sintax checking in {lang} of the document below, including section names if needed. Select the minimum context to be understable, around twenty words. Keep the same style and tone in the corrections, ignore literals in case of programming examples. Consider that some documents could have no grammar or sintax problems at all, if nothing is found don't hallucinate please. If no important problems are found, return an empty list []

# Also, consider that the document could have non-sense phrases in the middle, or typographic errors. This should be marked and suggestions to be done including remove the content.
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
#         prompt = """
# Your role in the review of this document is: {role}
# Document purpose: {purpose}

# Perform a grammar and sintaxis checking in {lang} of the document below, focus on minimal changes to make it correct. Write just the results in markdown, no extra titles or phrases. For each result use a classic "Where it says" / "it should say" convention and always remark corrections in bold format, as in this example:

# In section **[section name]**
#   * Where it says: ... This allows **reusing** of any study or tool applied to a specific instrument with **low** effort ...
#   * It should say: ... This allows **for the reuse** of any study or tool applied to a specific instrument with **little** effort ...

  
# The content to be analyzed is below:
# ========================
# {content}
# ========================

# Now provide the section/corrections:
# """

        prompt_template = PromptTemplate(
            input_variables=["role", "purpose", "lang", "content"],
            template=prompt
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        # result = chain.run(section=section_text)
        result = chain.run(role=self.my_role, purpose=self.purpose, lang=self.lang, content=content)
        return recover_json(result)
        

    def generate_hint(self, markdown_text: str) -> str:
        """
        Generate a hint based on the overall analysis of the document.
        
        :param markdown_text: The markdown document to analyze.
        :return: A generated hint as a string.
        """
        overall_hint = self.analyze_overall(markdown_text)
        return overall_hint
    
    
    
llm = LLMDocumentAgent(
    user_role="Expert in the topic of the document",
    purpose="Inferred from the document",
    lang="Inferred from the document"
)

# # Example usage when running this module directly
# if __name__ == "__main__":
#     sample_md = """
# # M1 Forces 🦾

# Web interface for M1 forces analysis done by Paranal Optics. This project is part of the ESO - Summer Internship Program 2025, Paranal Software Group.

# ## Deployment
# Run on: http://dev1-dev.pl.eso.org:8555

# ## Usage
# - **Choose TAR:** Select a TAR file from historical data.
# - **Upload New TAR File:** Upload a TAR file from your local storage.
# - **Run Program:** Execute the program to generate results (graphs and CSV data).
# - **Display Available Data:** Access previously processed files.

# ## Focus Mapping
# Similar to M1 Forces, with additional files such as:
# - .aberresult file
# - .defocusdata file
# - .fitAberrations file
# """
#     agent = LLMDocumentAgent(
#         your_role="Document Analysis Expert",
#         document_purpose="Provide hints and guidance for document usage and development"
#     )
#     overall_analysis = agent.analyze_overall(sample_md)
#     print("Overall Analysis:\n", overall_analysis)

#     usage_analysis = agent.analyze_section(sample_md, "Usage")
#     print("\nSection Analysis (Usage):\n", usage_analysis)
