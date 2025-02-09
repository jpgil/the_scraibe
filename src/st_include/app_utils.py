import streamlit as st
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
import time
import src.st_include.app_users as app_users
import src.st_include.app_docs as app_docs
import random

import yaml
import os
import hashlib

ph = None
def render_sidebar(pagefilename):
    """Sidebar for login/logout and user actions."""         
    global ph
    st.set_page_config(layout="wide", page_title="the scrAIbe")

    # Show notifications with notify(msg)
    _notify_show()
    
    with st.sidebar:
        # This container can be modified from the page later        
        st_sidebar = st.container()

        # Login line
        if "logged_in" not in st.session_state:
            app_users.render_user_loggedout()
        else:
            app_users.render_user_loggedin()
            
        return st_sidebar
            
    ph = st.sidebar.container()
                    
def notify(msg, switch=False):
    if 'notify_channel' not in st.session_state:
        st.session_state['notify_channel'] = [msg]
    else:
        st.session_state['notify_channel'].append(msg)

    if switch:
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
        
        

QUILL_MARKDOWN_TOOLBAR = [
    ["bold", "italic", "strike", "code"],  # Basic formatting
    [{"header": [1, 2, 3, 4, 5, 6, False]}],  # Headers (H1, H2, H3)
    [{"list": "ordered"}, {"list": "bullet"}, {"indent": "-1"}, {"indent": "+1"}],  # Lists
    ["blockquote", "code-block"],  # Block elements
    ["link", "image"],  # Links and images
    ["clean"],  # Remove formatting
]

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

# Scroll to here
# --------------
def scroll_to_here(anchor=""):
    global _last_scroll_to_here
    if not anchor:
        anchor = f"anchor{str(random.randint(100000, 999999))}"
    
    # Write the anchor
    st.markdown(f'<div id="{anchor}></div>', unsafe_allow_html=True)
    
    # Prepare to scroll to here
    _last_scroll_to_here = anchor
    
    # Schedule for later
    run_at_bottom(_scroll_to_here_last_call)

def _scroll_to_here_last_call():
    """Ensure the only one scroll to here is invoked"""
    global _last_scroll_to_here, _scroll_to_here_max_runs
    if _last_scroll_to_here and _scroll_to_here_max_runs>0:
        _scroll_to_here_max_runs -= 1
        js_code = f"""<script style="display: none; ">
            window.onload = function() {{
                var element = parent.document.getElementById("{_last_scroll_to_here}");
                if (element) {{
                    element.scrollIntoView({{ behavior: "smooth", block: "start" }});
                }}
            }};
        </script>"""
        components.html(js_code, height=0)
        st.code(f"Just wrote {js_code}", wrap_lines=True)
_scroll_to_here_max_runs = 1
_last_scroll_to_here = ""



_bottom_streamlit = []
def run_at_bottom(x):
    global _bottom_streamlit
    _bottom_streamlit.append(x)
    
def render_bottom_page():
    """Write the components at the end"""
    global _bottom_streamlit
    for st_piece in _bottom_streamlit:
        st_piece()
        
    