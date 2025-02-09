#!/usr/bin/env python3
"""
llm.py

A structured document analysis agent using LangChain.
This file imports configuration from settings.py to load credentials for OpenAI or Gemini.
It supports overall document analysis, section-specific analysis, and hint generation.
All inputs are assumed to be in markdown format.
"""

import re
import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from settings import settings

# Initialize the appropriate LLM based on configuration
if settings.llm_provider.lower() == "openai":
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    from langchain.llms import OpenAI
    default_llm = OpenAI(temperature=0)
elif settings.llm_provider.lower() == "gemini":
    # Here we assume a Gemini-compatible LLM is available in LangChain.
    # Replace 'GeminiLLM' with the actual class or integration details.
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
    from langchain.llms import GeminiLLM  # Assuming this exists or is implemented
    default_llm = GeminiLLM(temperature=0)
else:
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

class LLMDocumentAgent:
    def __init__(self, your_role: str, document_purpose: str, llm=None):
        """
        Initialize the document analysis agent.

        :param your_role: The role assigned to the agent (e.g., "Document Analysis Expert").
        :param document_purpose: The intended purpose of analyzing the document.
        :param llm: Optional LLM instance; if not provided, a default is used based on settings.
        """
        self.your_role = your_role
        self.document_purpose = document_purpose
        self.llm = llm if llm is not None else default_llm

    def set_configuration(self, your_role: str, document_purpose: str):
        """
        Update the agent's configuration.
        """
        self.your_role = your_role
        self.document_purpose = document_purpose

    def analyze_overall(self, markdown_text: str) -> str:
        """
        Perform an overall analysis of the complete markdown document.
        
        :param markdown_text: The entire document in markdown.
        :return: Analysis result as a string.
        """
        prompt = f"""
Your role is: {self.your_role}
Document purpose: {self.document_purpose}

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
Your role is: {self.your_role}
Document purpose: {self.document_purpose}

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

    def generate_hint(self, markdown_text: str) -> str:
        """
        Generate a hint based on the overall analysis of the document.
        
        :param markdown_text: The markdown document to analyze.
        :return: A generated hint as a string.
        """
        overall_hint = self.analyze_overall(markdown_text)
        return overall_hint

# Example usage when running this module directly
if __name__ == "__main__":
    sample_md = """
# M1 Forces 🦾

Web interface for M1 forces analysis done by Paranal Optics. This project is part of the ESO - Summer Internship Program 2025, Paranal Software Group.

## Deployment
Run on: http://dev1-dev.pl.eso.org:8555

## Usage
- **Choose TAR:** Select a TAR file from historical data.
- **Upload New TAR File:** Upload a TAR file from your local storage.
- **Run Program:** Execute the program to generate results (graphs and CSV data).
- **Display Available Data:** Access previously processed files.

## Focus Mapping
Similar to M1 Forces, with additional files such as:
- .aberresult file
- .defocusdata file
- .fitAberrations file
"""
    agent = LLMDocumentAgent(
        your_role="Document Analysis Expert",
        document_purpose="Provide hints and guidance for document usage and development"
    )
    overall_analysis = agent.analyze_overall(sample_md)
    print("Overall Analysis:\n", overall_analysis)

    usage_analysis = agent.analyze_section(sample_md, "Usage")
    print("\nSection Analysis (Usage):\n", usage_analysis)
