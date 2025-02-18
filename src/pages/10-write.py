import os 
import time
import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.stylable_container import stylable_container 
from streamlit_quill import st_quill
from src.st_include import app_utils
from src.st_include import app_users
from src.st_include import app_docs
from src.st_include import app_ai
from settings import settings

import src.core as scraibe
import markdownify

# import markdown
# import mistune

# https://www.webfx.com/tools/emoji-cheat-sheet/

def document_sanity_check(document_content):
    repaired = scraibe.repair_markdown_syntax(document_content)
    if repaired != document_content:
        scraibe.save_document(document_filename, document_content)
        app_utils.notify("Markdown was repaired")

# @st.cache_data(ttl=2)
def is_section_locked(document_filename, section_id):
    return scraibe.is_section_locked(document_filename, section_id)

def render_view_section(document_filename, document_content, section_id, user_current):
    global st_sidebar
    active_id = app_docs.editing_section_id()
    
    cols = st.columns([9, 1])
    
    # The content
    # -------
    with cols[0]:
        with st.container(border=False):
            if not active_id or active_id != section_id:
                #     app_utils.scroll_to_here()
                #     del(st.session_state['last_active_id'])
                section_content = scraibe.extract_section(document_content, section_id)
                st.markdown(section_content.strip())
            
    # Action buttons
    # ----------
    with cols[1]:
        with st.container(border=False):
            lock_user = is_section_locked(document_filename, section_id)

            # Display locked status or unlock if the current user is the locker.
            if lock_user:
                if lock_user == user_current:
                    scraibe.unlock_section(document_filename, section_id, user_current)
                    st.rerun()
                else:
                    st.markdown(f' ```{lock_user}```')
                    st_sidebar.markdown(f'⚠ ```Also editing: {lock_user}```')
            else:
                # Edit button
                if app_users.can_edit() and st.button("✍️", key=f"edit_{section_id}", type="secondary", use_container_width=False):
                        app_docs.set_editing_section_id(section_id)
                        # app_docs.set_selexcted_section_id(section_id)
                        st.rerun()

                # Tools button
                selected_id = app_docs.selected_section_id()
                is_selected = selected_id == section_id
                if st.button("☑️" if is_selected else "⬜", key=f"select_id_{section_id}", type="secondary"):
                    new_selected_id = None if is_selected else section_id
                    app_docs.set_selected_section_id(new_selected_id)


def render_edit_section(document_filename, document_content, active_id, user_current, sidebar):
    if not app_users.can_edit():
        return

    active_id = app_docs.editing_section_id()
    if not active_id:
        return
    
    st.session_state['last_active_id'] = active_id

    app_utils.scroll_to_here()
    if not scraibe.lock_section(document_filename, active_id, user_current):
        app_docs.set_editing_section_id(False)
        app_utils.notify(f'Section already locked by {scraibe.is_section_locked(document_filename, active_id)}', switch=__file__)

    # The Editor
    # --------
    section_content = scraibe.extract_section(document_content, active_id)

    # document_html = mistune.markdown(section_content)
    document_html = scraibe.to_html(section_content)
    quill_output = st_quill(
        value=document_html,
        html=True,
        toolbar=app_utils.QUILL_MARKDOWN_TOOLBAR,
        preserve_whitespace=False
        )
    new_html = app_utils.fix_quill_nested_lists( quill_output )
    new_markdown = markdownify.markdownify(new_html, heading_style='ATX', strip=['br'], bullets="*", newline_style="<br />")
    
    # Buttons
    # ------
    cols = st.columns(2)
    with cols[0]:
        if st.button("Save"):
            if section_content.strip() != new_markdown.strip():
                scraibe.save_section(document_filename, active_id, user_current, new_markdown)
            scraibe.unlock_section(document_filename, active_id, user_current)
            app_docs.set_editing_section_id(False)
            if section_content.strip() != new_markdown.strip():
                st.rerun()
            else:
                app_utils.notify("Nothing to save")
            
    with cols[1]:
        if st.button("Cancel editing"):
            def cancel_editing():
                scraibe.unlock_section(document_filename, active_id, user_current)
                app_docs.set_editing_section_id(False)
                st.rerun()
            if section_content.strip() != new_markdown.strip():
                app_utils.confirm_action("Cancel edition and discard changes?", cancel_editing)
            else:
                cancel_editing()

    def quill_js():
        js_code = """<script>
        var iframe = parent.document.querySelector('iframe');
        console.log("encontre iframes")
        if (iframe) {
        var doc = iframe.contentDocument || iframe.contentWindow.document;
        var styleElement = doc.createElement('style');
        styleElement.textContent = `
            .ql-editor {
                /* height: 400px !important;  /* Full viewport height */
                /* overflow: auto !important; /* Enable scrolling */
                font-family: "Source Sans Pro", sans-serif;
                font-size: 0.9rem;
                color: rgb(81, 83, 95);
                line-height: 1.5;
            }
            .ql-container.ql-snow {
                /*height: 425px;*/
            }
            .ql-editor p,
            .ql-editor ul,
            .ql-editor ol {
                margin-bottom: 1em;
            }
            .ql-editor h1,
            .ql-editor h2,
            .ql-editor h3,
            .ql-editor h4,
            .ql-editor h5 {
                margin-bottom: 1em;
                font-weight: bold;            
            }        
        `;
        doc.head.appendChild(styleElement);
        console.log("He agregado el elemento")
        }        </script>"""
        time.sleep(0.1)
        components.html(js_code, height=0)
        # st.write("Agregado")
    # app_utils.run_at_bottom(quill_js)
    # with st_sidebar:
    quill_js()

def render_selected_section(document_content):
    global st_sidebar
    section_id = app_docs.selected_section_id()
    document_filename = app_docs.active_document()
    
    if not section_id:
        return
    try:
        section_content = scraibe.extract_section(document_content, section_id)
        first_line = section_content.replace("#", "").splitlines()[0]
    except:
        app_docs.set_selected_section_id(False)
        st.rerun()

    with st_sidebar:
        st.code(first_line, language=None, wrap_lines=True)
        cols = st.columns([1,1])
        document_sections = scraibe.list_sections(document_content)
        if cols[0].button("☑️ Unselect", key=f"unselect2_{section_id}", use_container_width=True):
            app_docs.set_selected_section_id(False)

        if app_users.can_edit():                
            if section_id != document_sections[0]:
                if cols[1].button("❌ Delete", key=f"remove2_{section_id}", use_container_width=True):
                    app_utils.confirm_action(
                        "Delete this section?", 
                        scraibe.delete_section, 
                        document_filename, section_id, user_current)
        
        AI_section_toolslist = ['', 'Analyse in context', 'Suggest content']
        cols = st.columns([4,1])
        AI_task = cols[0].selectbox('AI section', AI_section_toolslist, label_visibility="collapsed", key=f"AI_section_{section_id}")
        if cols[1].button("💡"):
            if AI_task == 'Analyse in context':
                result = scraibe.llm.analyse_section_in_context(document_content, section_content)
                scraibe.llm.remember(AI_task, section_id, document_filename, result)
            elif AI_task == 'Suggest content':
                result = scraibe.llm.suggest_section_content(document_content, section_content)
                scraibe.llm.remember(AI_task, section_id, document_filename, result)
        
        if AI_task != '':
            with st.container():
                result = scraibe.llm.remember(AI_task, section_id, document_filename)
                if not result:
                    st.write("Press 💡 to execute")
                else:
                    st.write(result)
                
    st_sidebar.markdown("---")
    

def render_AI_document_tools(*args, **kwargs):
    # General AI tools:
    # -------------            
    document_content = kwargs["document_content"]
    # Create tabs
    st.header("AI tools")
    tablist = {
        "Grammar": app_ai.render_review_grammar,
        "Content Assessment" : app_ai.render_content_assessment,
        "Questions": app_ai.render_none,
        "Configure AI": app_ai.render_configure_AI,
    }
    
    tabs = st.tabs(tablist.keys())

    # Style Tab
    for i in range(len(tablist)):
        with tabs[i]:
            key = list(tablist.keys())[i]
            # st.subheader(key)
            tablist[key](st_sidebar=st_sidebar, document_content=document_content, document_meta=document_meta)




def render_download_options():
    import tempfile
    from markdown_pdf import MarkdownPdf, Section


    st.header("Download")
    filename = app_docs.active_document()
    content = scraibe.load_document_nolabels(filename)

    cols = st.columns(3)
    with cols[0]:
        if st.button("PDF", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile: 
                pdf = MarkdownPdf()
                pdf.meta["title"] = 'Title'
                pdf.add_section(Section(content, toc=False))
                pdf.save(tmpfile.name)
                st.session_state[f"generated_ftype_for_{filename}"] = tmpfile.name
                
    with cols[1]:
        if st.button("MD", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8") as tmpfile:
                tmpfile.write(content) 
                st.session_state[f"generated_ftype_for_{filename}"] = tmpfile.name

    @st.dialog("Download the file")
    def download_dialog():
        global document_filename
        file = st.session_state.get(f"generated_ftype_for_{document_filename}")
        if not file:
            st.rerun()
        ftype = file.split(".")[-1]
        ftypename = app_docs.active_document()[:-3]+"."+ftype
        with open(file, "rb") as f:
            file_bytes = f.read()
        if st.download_button(
            label=f"Download {ftypename}",
            data=file_bytes,
            file_name=ftypename,
            mime=f"application/{ftype}"
        ):
            os.remove(file)
            st.session_state[f"generated_ftype_for_{document_filename}"] = False
            st.rerun()
        if st.button("Cancel"):
            os.remove(file)
            st.session_state[f"generated_ftype_for_{document_filename}"] = False
            st.rerun()
   
    if st.session_state.get(f"generated_ftype_for_{document_filename}"):
        # app_utils.run_at_bottom(download_dialog)
        download_dialog()
                
        
if __name__ == "__main__":
    
    st_sidebar = app_utils.render_sidebar(__file__)
    
    # Check document selection 
    # --------------
    if not app_users.Im_logged_in():
        app_utils.notify("Login to see documents", switch="dashboard.py")                      
    if not app_docs.active_document():
        app_utils.notify("Select a document to write", switch="dashboard.py")
    if not app_users.can_view():
        app_utils.notify("Not authorized", switch="dashboard.py")
    
    user_current = app_users.user()

    # All good, let's show it
    document_filename = app_docs.active_document()
    document_meta = app_docs.filter_documents_for_user(user_current).get(document_filename)        
    document_content = scraibe.load_document(document_filename)
    document_sections = scraibe.list_sections(document_content)
    
    # Configure AI
    # st.write(document_meta)
    scraibe.llm.role = document_meta.get("role", scraibe.llm.role)
    scraibe.llm.purpose = document_meta.get("purpose", scraibe.llm.purpose)
    scraibe.llm.lang = document_meta.get("lang", scraibe.llm.lang)
            
    # Step 0: Sanity check
    # ---------
    if app_users.can_edit():
        document_sanity_check(document_content)

    editing_section_id = app_docs.editing_section_id()
    
    scraibe.llm.role = document_meta.get("role", scraibe.llm.role)

    # Display sections
    # --------
            
    with stylable_container(key="document_content", css_styles="""
 {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    line-height: 1.6;
    color: #24292e;
    background-color: #FAFAFA;
    margin: 20px 0;
    padding: 1em;
        
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        line-height: 1.25;
        margin-bottom: 16px;
    }

    h1 {
        font-size: 2em;
        border-bottom: 1px solid #e1e4e8;
        padding-bottom: 0.3em;
    }

    h2 {
        font-size: 1.5em;
        border-bottom: 1px solid #e1e4e8;
        padding-bottom: 0.3em;
    }

    h3 {
        font-size: 1.25em;
    }

    h4 {
        font-size: 1em;
    }

    ul, ol {
        padding-left: 2em;
    }

    li {
        margin-bottom: 4px;
    }

    pre {
        background-color: #f6f8fa;
        padding: 16px;
        border-radius: 6px;
        font-size: 85%;
        overflow: auto;
        line-height: 1.45;
    }

    code {
        font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, Courier, monospace;
        background-color: #f6f8fa;
        padding: 3px 6px;
        border-radius: 3px;
        font-size: 85%;
    }

    blockquote {
        color: #6a737d;
        border-left: 4px solid #dfe2e5;
        padding: 0 1em;
        margin: 0;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 16px;
    }

    th, td {
        padding: 8px;
        border: 1px solid #dfe2e5;
    }

    th {
        background-color: #f6f8fa;
        font-weight: 600;
    }

    a {
        color: #0366d6;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }
}                           
        """ ):
        with st.expander(document_filename, expanded=True):

            for section_id in document_sections:
                st.markdown(f'<div id="section{section_id}"></div>', unsafe_allow_html=True)
                if editing_section_id == section_id:
                    render_edit_section(document_filename, document_content, section_id, user_current, st_sidebar)
                else:
                    render_view_section(document_filename, document_content, section_id, user_current)

    with st.expander("💡 AI Writting Tools"):
        render_AI_document_tools(document_content=document_content)

    
    with st.expander("Download formats"):
        render_download_options()

    render_selected_section(document_content)


    # app_utils.render_bottom_page()
    
    
    