import streamlit as st
import streamlit.components.v1 as components
from streamlit_quill import st_quill
from src.st_include import utils
import src.st_include.users as users
import src.st_include.documents as documents
import src.core as scraibe
import markdownify

import markdown
import mistune

if __name__ == "__main__":
    utils.sidebar(__file__)
    
    # Check document selection 
    # --------------
    if not users.Im_logged_in():
        utils.notify("Login to see documents", switch="dashboard.py")    
                  
    current_user = st.session_state.get("username")    
    filtered_docs = documents.filter_documents_for_user(current_user)

    if not filtered_docs:
        utils.notify("You should create your first document", switch="dashboard.py")
    if st.session_state.get("document_file") not in filtered_docs:
        utils.notify("Select a document to write", switch="dashboard.py")

    # All good, let's show it
    document_active = documents.active_document()
    doc_meta = filtered_docs[document_active]
    document_content = scraibe.load_document(document_active)
    document_sections = scraibe.list_sections(document_content)
    
    # Obtain the current user's permission
    document_permission = None
    for user in doc_meta['users']:
        if user['name'] == current_user:
            document_permission = user['permission']
            
    # Step 0: add sections
    # ---------
    if document_permission in ['editor', 'admin', 'creator']:
        repaired = scraibe.repair_markdown_syntax(document_content)
        if repaired != document_content:
            scraibe.save_document(document_active, document_content)
            utils.notify("Markdown was repaired")


    # Viewer mode: Show document and action buttons
    # -------------            
    active_id = documents.active_section_id()
    if not active_id:
        # st_ids = {}
        for section_id in document_sections:
            cols = st.columns([8, 1])
            
            # The content
            # -------
            with cols[0]:
                with st.container(border=True):
                    if not active_id or active_id != section_id:
                        last_active_id = st.session_state.get('last_active_id', False)
                        # if last_active_id in document_sections and section_id == document_sections[document_sections.index(last_active_id)-1]:
                        if section_id == st.session_state.get('last_active_id'):
                            utils.scroll_to_here()
                            del(st.session_state['last_active_id'])
                        section_content = scraibe.extract_section(document_content, section_id)
                        st.markdown(section_content.strip())
                    
            # Action buttons
            # ----------
            with cols[1]:
                if document_permission in ['editor', 'admin', 'creator']:
                    with st.container(border=True):
                        lock_user = scraibe.is_section_locked(document_active, section_id)
                        if lock_user:
                            if lock_user == current_user:
                                scraibe.unlock_section(document_active, section_id, current_user)
                                st.rerun()
                            else:
                                st.markdown(f' ```{lock_user}```')
                        else:
                            if st.button(":feather:", key=f"edit_{section_id}", use_container_width=True):
                                documents.set_active_section_id(section_id)
                                st.rerun()
                            # if st.button("❌", key=f"remove_{section_id}", use_container_width=True):
                            # Avoid remove first section
                            if section_id != document_sections[0]:
                                if st.button("🗑️", key=f"remove_{section_id}", use_container_width=True):
                                    # scraibe.delete_section(document_active, section_id, current_user)
                                    utils.confirm_action(
                                        "Delete this section?", 
                                        scraibe.delete_section, 
                                        document_active, section_id, current_user)
                                    
        st.code("The document ends here")
        
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


    # Edit section mode:
    # -------------            
    if active_id:
        st.session_state['last_active_id'] = active_id
        # utils.scroll_to_here()
        if not scraibe.lock_section(document_active, active_id, current_user):
            documents.set_active_section_id(False)
            utils.notify(f'Section already locked by {scraibe.is_section_locked(document_active, active_id)}', switch=__file__)

        # The Editor
        # --------
        section_content = scraibe.extract_section(document_content, active_id)

        # document_html = markdown.markdown(
        #     section_content,
        #         extensions=["extra", "tables", "footnotes", "md_in_html", "nl2br", "attr_list"]
        #     )
        # document_html = document_html.replace("<p>", "<br /><p>")
        # document_html = document_html.replace("<ul>", "<br /><ul>")

        document_html = mistune.markdown(section_content)
        # document_html = document_html.replace("<p>", "<br /><p>")
        # document_html = document_html.replace("<ul>", "<br /><ul>")
        # document_html = document_html.replace("<ol>", "<br /><ol>")

        # st.code(document_html, wrap_lines=True)

        quill_output = st_quill(
            value=document_html,
            html=True,
            toolbar=utils.QUILL_MARKDOWN_TOOLBAR,
            preserve_whitespace=False
            )
        # st.code(quill_output, wrap_lines=True)
        new_html = utils.fix_quill_nested_lists( quill_output )
        new_markdown = markdownify.markdownify(new_html, heading_style='ATX', strip=['br'], bullets="*", newline_style="<br />")
        # st.code(new_html, wrap_lines=True)
        # st.markdown(new_html, unsafe_allow_html=True)
        
        # Buttons
        # ------
        cols = st.columns(2)
        with cols[0]:
            if st.button("Save"):
                scraibe.save_section(document_active, active_id, current_user, new_markdown)
                scraibe.unlock_section(document_active, active_id, current_user)
                documents.set_active_section_id(False)
                st.rerun()
                
        with cols[1]:
            if st.button("Cancel editing"):
                def cancel_editing():
                    scraibe.unlock_section(document_active, active_id, current_user)
                    documents.set_active_section_id(False)
                utils.confirm_action("Cancel edition and discard changes?", cancel_editing)

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
        
        
    # if "messages" not in st.session_state:
    #     st.session_state.messages = []
    # # Chat experiment
    # with st.sidebar.container(border=True):
    #     # Build the HTML for all messages
    #     chat_html = '<div class="fixed-height">'
    #     for message in st.session_state.messages:
    #         # Customize the HTML as needed; this is a simple example.
    #         chat_html += f"<p><strong>{message['role']}:</strong> {message['content']}</p>"
    #     chat_html += '</div>'

    #     # Render the fixed container with the chat HTML
    #     st.markdown(
    #         """
    #         <style>
    #         .fixed-height {
    #             height: 300px;
    #             overflow: auto;
    #         }
    #         </style>
    #         """,
    #         unsafe_allow_html=True,
    #     )
    #     st.markdown(chat_html, unsafe_allow_html=True)

    #     if user_input := st.chat_input("Type your message here..."):
    #         st.session_state.messages.append({"role": "user", "content": user_input})
    #         # Here you can add the logic to handle the user input and generate a response
    #         # For example, you can call a function to get a response from a chatbot model
    #         response = "This is a placeholder response."
    #         st.session_state.messages.append({"role": "bot", "content": response})
    #         st.rerun()
    
    
    if st.session_state.get("force rerun"):
        import time
        del(st.session_state['force rerun'])
        st.code("Re run")
        time.sleep(0.5)
        st.rerun()
