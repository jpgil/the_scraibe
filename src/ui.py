import streamlit as st
import src.st_include.users as users
import src.st_include.utils as utils
import src.st_include.documents as documents

if __name__ == "__main__":

    # UI Setup
    utils.sidebar(__file__)
    # st.title("the scrAIbe")

    # if not users.Im_logged_in():
        # st.image("images/the_scribe.png", width=300)

    col1, col2 = st.columns(2)

    with col1:
        st.image("images/the_scribe.png", width=300)

    with col2:
        st.markdown(
            """
            <style>
            .hero-container {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px;
            }
            .hero-text {
                # max-width: 50%;
                font-size: 20px;
            }
            .hero-tagline {
                font-size: 40px;
                font-weight: bold;
                color: #2E86C1;
            }

            </style>
            <div class="hero-container">
                <div class="hero-text">
                    <div class="hero-tagline">the scrAIbe</div>
                    <p class="hero-tagline">Precision Writing, Supercharged by AI</p>
                    <p>the scrAIbe isn’t just a writing tool—it’s your AI-powered assistant for structured, multi-user collaboration. 
                    From real-time refinement to deep content insights, every document benefits from the intelligence of modern AI.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )    

    if users.Im_logged_in():

        
        current_user = st.session_state.get("username")
        filtered_docs = list(documents.filter_documents_for_user(current_user))
        if filtered_docs:
            st.subheader("Your documents", divider=False)
            st.selectbox("Choose a document to continue editing", [""] + filtered_docs)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Upload Document")
            filename = st.file_uploader(label="Document Filename (e.g., document01.md)", key="upload_doc_filename")
            creator = st.session_state.get("username", "")
            if st.button(label="Upload Document"):
                if filename and creator:
                    utils.notify("Not implemented yet")
                    # if documents.add_document(filename, creator):
                    #     utils.notify(f"Document {filename} created successfully!", switch="pages/01-documents.py")
                else:
                    st.error("Filename and creator are required.")

        with col2:
            st.subheader("Create New Document")
            filename = st.text_input(label="Document Filename (e.g., document01.md)", key="doc_filename")
            creator = st.session_state.get("username", "")
            if st.button(label="Create Document"):
                if filename and creator:
                    if documents.add_document(filename, creator):
                        utils.notify(f"Document {filename} created successfully!", switch="pages/01-documents.py")
                else:
                    st.error("Filename and creator are required.")

        if users.Im_admin():
            users.render_user_management()
            
    else:
        st.subheader("Don't have an user yet?")
        st.write("Create your user")

    # Check if no users exist in the YAML file
    if not users.load_users():
        users.render_create_admin()
            