import streamlit as st
import streamlit.components.v1 as components
from streamlit_quill import st_quill
from src.st_include import app_utils
from src.st_include import app_users
from src.st_include import app_docs
import src.core as scraibe
import markdownify

# import markdown
import mistune

def render_sanity_check(document_content):
    repaired = scraibe.repair_markdown_syntax(document_content)
    if repaired != document_content:
        scraibe.save_document(document_filename, document_content)
        app_utils.notify("Markdown was repaired")


def render_view_section(document_filename, document_content, section_id, user_current, user_permission):
    active_id = app_docs.active_section_id()
    
    cols = st.columns([8, 1])
    
    # The content
    # -------
    with cols[0]:
        with st.container(border=True):
            if not active_id or active_id != section_id:
                # last_active_id = st.session_state.get('last_active_id', False)
                # if last_active_id in document_sections and section_id == document_sections[document_sections.index(last_active_id)-1]:
                # if section_id == st.session_state.get('last_active_id'):
                #     app_utils.scroll_to_here()
                #     del(st.session_state['last_active_id'])
                section_content = scraibe.extract_section(document_content, section_id)
                st.markdown(section_content.strip())
            
    # Action buttons
    # ----------
    with cols[1]:
        if user_permission in ['editor', 'admin', 'creator']:
            with st.container(border=True):
                lock_user = scraibe.is_section_locked(document_filename, section_id)
                if lock_user:
                    if lock_user == user_current:
                        scraibe.unlock_section(document_filename, section_id, user_current)
                        st.rerun()
                    else:
                        st.markdown(f' ```{lock_user}```')
                else:
                    if st.button(":feather:", key=f"edit_{section_id}", use_container_width=True):
                        app_docs.set_active_section_id(section_id)
                        st.rerun()
                    # Avoid remove first section
                    if section_id != document_sections[0]:
                        if st.button("🗑️", key=f"remove_{section_id}", use_container_width=True):
                            # scraibe.delete_section(document_active, section_id, current_user)
                            app_utils.confirm_action(
                                "Delete this section?", 
                                scraibe.delete_section, 
                                document_filename, section_id, user_current)


def render_edit_section(document_filename, document_content, active_id, user_current, user_permission):
    if user_permission not in ['editor', 'admin', 'creator']:
        return

    active_id = app_docs.active_section_id()
    if not active_id:
        return
    
    st.session_state['last_active_id'] = active_id

    # utils.scroll_to_here()
    if not scraibe.lock_section(document_filename, active_id, user_current):
        app_docs.set_active_section_id(False)
        app_utils.notify(f'Section already locked by {scraibe.is_section_locked(document_filename, active_id)}', switch=__file__)

    # The Editor
    # --------
    section_content = scraibe.extract_section(document_content, active_id)

    document_html = mistune.markdown(section_content)
    # document_html = document_html.replace("<p>", "<br /><p>")
    # document_html = document_html.replace("<ul>", "<br /><ul>")
    # document_html = document_html.replace("<ol>", "<br /><ol>")

    # st.code(document_html, wrap_lines=True)

    quill_output = st_quill(
        value=document_html,
        html=True,
        toolbar=app_utils.QUILL_MARKDOWN_TOOLBAR,
        preserve_whitespace=False
        )
    # st.code(quill_output, wrap_lines=True)
    new_html = app_utils.fix_quill_nested_lists( quill_output )
    new_markdown = markdownify.markdownify(new_html, heading_style='ATX', strip=['br'], bullets="*", newline_style="<br />")
    # st.code(new_html, wrap_lines=True)
    # st.markdown(new_html, unsafe_allow_html=True)
    
    # Buttons
    # ------
    cols = st.columns(2)
    with cols[0]:
        if st.button("Save"):
            scraibe.save_section(document_filename, active_id, user_current, new_markdown)
            scraibe.unlock_section(document_filename, active_id, user_current)
            app_docs.set_active_section_id(False)
            st.rerun()
            
    with cols[1]:
        if st.button("Cancel editing"):
            def cancel_editing():
                scraibe.unlock_section(document_filename, active_id, user_current)
                app_docs.set_active_section_id(False)
                st.rerun()
            if section_content.strip() != new_markdown.strip():
                app_utils.confirm_action("Cancel edition and discard changes?", cancel_editing)
            else:
                cancel_editing()

    # Dev option
    if st.checkbox("(dev) original / modified markdown"):
        cols = st.columns(2)
        with cols[0]:
            st.code(section_content, wrap_lines=True)
        with cols[1]:
            st.code(new_markdown, wrap_lines=True)



    js_code = """<script>
    var iframe = parent.document.querySelector('iframe');
    console.log("encontre iframes")
    if (iframe) {
    var doc = iframe.contentDocument || iframe.contentWindow.document;
    var styleElement = doc.createElement('style');
    styleElement.textContent = `
        .ql-editor {
            height: 300px !important;  /* Full viewport height */
            overflow: auto !important; /* Enable scrolling */
        }
        .ql-container.ql-snow {
            height: auto;
        }
    `;
    doc.head.appendChild(styleElement);
    console.log("He agregado el elemento")
    }        </script>"""
    components.html(js_code, height=0)


def render_AI_document_tools():
    # General AI tools:
    # -------------            
    # Create tabs
    st.header("AI tools")
    tab1, tab2, tab3, tab4 = st.tabs(["Style", "Reviewer", "Grammar", "Questions"])

    # Download Tab
    with tab1:
        st.text_input("Define the style")
        st.button("Check the style")
    # Reviewer Tab
    with tab2:
        st.text_input("Describe who will assess your document")
        st.button("Ask reviewer")

    # Grammar Tab
    with tab3:
        st.button("Review grammar")

    # Questions Tab
    with tab4:
        st.text_input("Ask any question regarding your document")
        st.button("Ask your question")

    st.header("Download")
    cols = st.columns(3)
    with cols[0]:
        st.button("PDF", use_container_width=True)
    with cols[1]:
        st.button("docx", use_container_width=True)
    with cols[2]:
        st.button("MD", use_container_width=True)
        
        
        
if __name__ == "__main__":
    app_utils.sidebar(__file__)
    
    # Check document selection 
    # --------------
    if not app_users.Im_logged_in():
        app_utils.notify("Login to see documents", switch="dashboard.py")    
                  
    user_current = st.session_state.get("username")    
    filtered_docs = app_docs.filter_documents_for_user(user_current)

    if not filtered_docs:
        app_utils.notify("You should create your first document", switch="dashboard.py")
    if st.session_state.get("document_file") not in filtered_docs:
        app_utils.notify("Select a document to write", switch="dashboard.py")

    # All good, let's show it
    document_filename = app_docs.active_document()
    document_meta = filtered_docs[document_filename]
    document_content = scraibe.load_document(document_filename)
    document_sections = scraibe.list_sections(document_content)
    
    # Obtain the current user's permission
    user_permission = None
    for user in document_meta['users']:
        if user['name'] == user_current:
            user_permission = user['permission']
            
            
    # Step 0: Sanity check
    # ---------
    if user_permission in ['editor', 'admin', 'creator']:
        render_sanity_check(document_content)


    # Viewer mode: Show document and action buttons
    # -------------            
    active_id = app_docs.active_section_id()
                                        
    for section_id in document_sections:
        # Edit section mode:
        # -------------            
        if active_id == section_id:
            render_edit_section(document_filename, document_content, section_id, user_current, user_permission)
        else:
            render_view_section(document_filename, document_content, section_id, user_current, user_permission)

    st.code("The document ends here")
    render_AI_document_tools()

        
    # # Edit section mode:
    # # -------------            
    # if active_id:
    #     render_edit_section(document_filename, document_content, active_id, user_current, user_permission)


    if st.session_state.get("force rerun"):
        import time
        del(st.session_state['force rerun'])
        st.code("Re run")
        time.sleep(0.5)
        st.rerun()
