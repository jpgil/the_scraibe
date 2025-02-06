import streamlit as st
from src.st_include import utils
import src.st_include.users as users
import src.st_include.documents as documents
import src.core as scraibe


if __name__ == "__main__":
    utils.sidebar(__file__)
    if not users.Im_logged_in():
        utils.notify("Login to see documents", switch="ui.py")
    st.title("Documents Dashboard")
    documents.render_document_management()
