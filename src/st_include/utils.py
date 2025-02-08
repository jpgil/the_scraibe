import streamlit as st
import streamlit.components.v1 as components
import time
import src.st_include.users as users
import src.st_include.documents as documents

import yaml
import os
import hashlib

ph = None
def sidebar(pagefilename):
    global ph
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
            
    ph = st.sidebar.container()
                    
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


from bs4 import BeautifulSoup
def fix_quill_nested_lists_v1(html):
    soup = BeautifulSoup(html, "html.parser")

    for list_tag in soup.find_all(["ul", "ol"]):  # Find all lists
        list_items = list_tag.find_all("li", recursive=False)  # Get only top-level LIs
        stack = [[]]  # Stack to track nesting levels

        for li in list_items:
            indent_level = 0
            for class_name in li.get("class", []):
                if class_name.startswith("ql-indent-"):
                    indent_level = int(class_name.split("-")[2])

            # Ensure the stack has enough levels
            while len(stack) <= indent_level:
                stack.append([])

            # Reduce stack if necessary
            while len(stack) > indent_level + 1:
                stack.pop()

            if indent_level > 0 and stack[indent_level - 1]:
                parent_li = stack[indent_level - 1][-1]  # Get last item in parent level
                existing_sublist = parent_li.find(["ul", "ol"])
                
                if not existing_sublist:
                    # Create a new nested list if none exists
                    new_sublist = soup.new_tag(list_tag.name)
                    parent_li.append(new_sublist)
                else:
                    new_sublist = existing_sublist  # Reuse existing nested list
                
                new_sublist.append(li)  # Move current LI into the nested list
                stack[indent_level].append(li)  # Add to stack at correct level
            else:
                stack[0].append(li)  # Keep top-level items at root

        # Clear the original list and append the corrected structure
        list_tag.clear()
        for item in stack[0]:
            list_tag.append(item)

    return str(soup)

def fix_quill_nested_lists(html):
    soup = BeautifulSoup(html, "html.parser")

    for list_tag in soup.find_all(["ul", "ol"]):  # Process both ordered and unordered lists
        list_items = list_tag.find_all("li", recursive=False)
        stack = [[]]  # Stack for nested lists

        for li in list_items:
            indent_level = 0
            for class_name in li.get("class", []):
                if class_name.startswith("ql-indent-"):
                    indent_level = int(class_name.split("-")[2])

            # Ensure stack has enough levels
            while len(stack) <= indent_level:
                stack.append([])

            # Reduce stack depth if needed
            while len(stack) > indent_level + 1:
                stack.pop()

            if indent_level > 0 and stack[indent_level - 1]:
                parent_li = stack[indent_level - 1][-1]
                existing_sublist = parent_li.find(["ul", "ol"])

                if not existing_sublist:
                    # Use the same list type as the current parent
                    new_sublist = soup.new_tag(list_tag.name)
                    parent_li.append(new_sublist)
                else:
                    new_sublist = existing_sublist

                new_sublist.append(li)  # Add nested <li> correctly
                stack[indent_level].append(li)
            else:
                stack[0].append(li)

        # Clear the original list and insert corrected structure
        list_tag.clear()
        for item in stack[0]:
            list_tag.append(item)

    return str(soup)


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
    js_code = f"""<script style="display: none; ">
        window.onload = function() {{
            var element = parent.document.getElementById("scrolltohere");
            if (element) {{
                element.scrollIntoView({{ behavior: "smooth", block: "start" }});
            }}
        }};
    </script>"""
    components.html(js_code, height=0)
    st.session_state['force rerun'] = True