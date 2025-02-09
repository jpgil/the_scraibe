import streamlit as st
from src.core.llm import *


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
st.write("Overall Analysis:\n", overall_analysis)

usage_analysis = agent.analyze_section(sample_md, "Usage")
st.write("\nSection Analysis (Usage):\n", usage_analysis)
