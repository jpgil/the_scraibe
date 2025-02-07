import streamlit as st
import streamlit.components.v1 as components
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
        
        
# QUILL_TOOLBAR = [
#     [
#         "bold", "italic", "underline", "strike",
#         {"script": "sub"},
#         {"script": "super"},
#     ],
#     [
#         {"background": []},
#         {"color": [] },
#     ],          
#     [
#         {"list": "ordered"},
#         {"list": "bullet"},
#         {"indent": "-1"},
#         {"indent": "+1"},
#         {"align": []},
#     ],
#     [
#         {"header": 1},
#         {"header": 2},
#         {"header": [1, 2, 3, 4, 5, 6, False]},
#         {"size": ["small", False, "large", "huge"]},
#     ],
#     [
#         "formula", "blockquote", "code", "code-block", "clean"
#     ],
#     [
#         "link", "image"
#     ],
#     [
#         {"font": []}
#     ],
# ]
QUILL_MARKDOWN_TOOLBAR = [
    ["bold", "italic", "strike", "code"],  # Basic formatting
    [{"header": [1, 2, 3, 4, 5, 6, False]}],  # Headers (H1, H2, H3)
    [{"list": "ordered"}, {"list": "bullet"}, {"indent": "-1"}, {"indent": "+1"}],  # Lists
    ["blockquote", "code-block"],  # Block elements
    ["link", "image"],  # Links and images
    ["clean"],  # Remove formatting
]

@st.dialog("Confirm")
def confirm_action(question, func, *args, **params):
    st.write(question)
    cols = st.columns(2)
    error = False
    with cols[0]:
        if st.button("Yes", use_container_width=True):
            try:
                func(*args, **params)
                notify(f'{question} YES')
                st.rerun()
            except Exception as ex:
                error = ex
    with cols[1]:
        if st.button("No", use_container_width=True):
            notify('Cancelled')
            st.rerun()
    if error:
        st.error(error)

def scroll_to_here():
    st.markdown(f'<div id="scrolltohere"></div>', unsafe_allow_html=True)
    js_code = f"""
    <script>
        window.onload = function() {{
            var element = parent.document.getElementById("scrolltohere");
            if (element) {{
                element.scrollIntoView({{ behavior: "smooth", block: "start" }});
            }}
        }};
    </script>
    """
    components.html(js_code, height=0)
