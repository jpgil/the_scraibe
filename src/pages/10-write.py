import os 
import time
import streamlit as st
import streamlit.components.v1 as components
from streamlit_quill import st_quill
from src.st_include import app_utils
from src.st_include import app_users
from src.st_include import app_docs
from src.st_include import app_ai

import src.core as scraibe
import markdownify

# import markdown
# import mistune

def document_sanity_check(document_content):
    repaired = scraibe.repair_markdown_syntax(document_content)
    if repaired != document_content:
        scraibe.save_document(document_filename, document_content)
        app_utils.notify("Markdown was repaired")


def render_view_section(document_filename, document_content, section_id, user_current):
    global st_sidebar
    active_id = app_docs.editing_section_id()
    
    cols = st.columns([8, 1])
    
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
        with st.container(border=True):
            lock_user = scraibe.is_section_locked(document_filename, section_id)
            if lock_user:
                if lock_user == user_current:
                    scraibe.unlock_section(document_filename, section_id, user_current)
                    st.rerun()
                else:
                    st.markdown(f' ```{lock_user}```')
                    st_sidebar.markdown(f'⚠ ```Also editing: {lock_user}```')
                    
            else:
                # button EDIT
                if app_users.can_edit():
                    if st.button(":feather:", key=f"edit_{section_id}", use_container_width=True):
                        app_docs.set_editing_section_id(section_id)
                        # app_docs.set_selexcted_section_id(section_id)
                        st.rerun()
                        
                # button TOOLS
                selected_id = app_docs.selected_section_id()
                if selected_id != section_id:
                    if st.button("⬜", key=f"selected_id{section_id}"):
                        app_docs.set_selected_section_id(section_id)
                else:
                    if st.button("☑️", key=f"selected_id{section_id}"):
                        app_docs.set_selected_section_id(None)


def render_edit_section(document_filename, document_content, active_id, user_current):
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
    app_utils.run_at_bottom(quill_js)


def render_selected_section(document_content):
    global st_sidebar
    section_id = app_docs.selected_section_id()
    if not section_id:
        return
    try:
        first_line = scraibe.extract_section(document_content, section_id).replace("#", "").splitlines()[0]
    except:
        app_docs.set_selected_section_id(False)
        st.rerun()

    with st_sidebar:
        st.markdown(f"""
```
{first_line}
                    """)        
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
        
        AI_section_toolslist = ['Analyse content', 'Suggest content', 'Versions', 'Your role']
        cols = st.columns([3,1])
        selected_AI_section_toolslist = cols[0].selectbox('AI section', AI_section_toolslist, label_visibility="collapsed")
        if cols[1].button("💡 AI"):
            st.write(f"Your selected AI tool is {AI_section_toolslist}.\n Here we will write the output of the tool.")
                    
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
            tablist[key](st_sidebar=st_sidebar, document_content=document_content)




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
    
    user_current = st.session_state.get("username")   

    # All good, let's show it
    document_filename = app_docs.active_document()
    document_content = scraibe.load_document(document_filename)
    document_sections = scraibe.list_sections(document_content)
            
    # Step 0: Sanity check
    # ---------
    if app_users.can_edit():
        document_sanity_check(document_content)

    editing_section_id = app_docs.editing_section_id()

    # Display sections
    # --------
    with st.expander(document_filename, expanded=True):
        with st.container(border=False):
            for section_id in document_sections:
                st.markdown(f'<div id="section{section_id}"></div>', unsafe_allow_html=True)
                if editing_section_id == section_id:
                    render_edit_section(document_filename, document_content, section_id, user_current)
                else:
                    render_view_section(document_filename, document_content, section_id, user_current)

    with st.expander("💡 AI Writting Tools"):
        render_AI_document_tools(document_content=document_content)

    
    with st.expander("Download formats"):
        render_download_options()

    render_selected_section(document_content)


    app_utils.render_bottom_page()