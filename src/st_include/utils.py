import streamlit as st
import time
import src.st_include.users as users
import src.st_include.documents as documents

import yaml
import os
import hashlib


def sidebar(pagefilename):
    st.set_page_config(layout="wide", page_title="the scrAIbe")
    _notify_show()
    """Sidebar for login/logout and user actions."""         
    
    with st.sidebar:
        if "10-write.py" in pagefilename:
            current_user = st.session_state.get("username")
            filtered_docs = [""] + list(documents.filter_documents_for_user(current_user))
            if filtered_docs:
                if st.session_state.get("document_file") in filtered_docs:
                    selected_document_index = filtered_docs.index(st.session_state["document_file"])
                else:
                    selected_document_index = 0
                st.session_state["document_file"] = st.selectbox(
                    "Choose a document to continue editing", 
                    filtered_docs,
                    index=selected_document_index
                    )

        if "logged_in" not in st.session_state:
            users.render_user_loggedout()
        else:
            users.render_user_loggedin()
                    
def notify(msg, switch=False):
    if 'notify_channel' not in st.session_state:
        st.session_state['notify_channel'] = [msg]
    else:
        st.session_state['notify_channel'].append(msg)

    if switch:
        # st.rerun()
        st.switch_page(switch)
        st.stop()
    else:
        st.rerun()

def _notify_show():
    if 'notify_channel' in st.session_state:
        for msg in st.session_state['notify_channel']:
            st.toast(msg)
            time.sleep(0.5)
        st.session_state['notify_channel'] = []    