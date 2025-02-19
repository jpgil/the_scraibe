import streamlit as st
import src.st_include.app_users as app_users
import src.st_include.app_utils as app_utils
import src.st_include.app_docs as app_docs

if __name__ == "__main__":

    # UI Setup
    app_utils.render_sidebar(__file__)
    
    col1, col2 = st.columns(2)
    with col1:
        # st.image("images/the_scribe.png", width=300)
        st.image("images/the_scribe-300.png")

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
                color: #FF4B4B;
            }

            </style>
            <div class="hero-container">
                <div class="hero-text">
                    <div class="hero-tagline">the scrAIbe</div>
                    <p class="hero-tagline">Markdown supercharged by AI</p>
                    <p>the scrAIbe is your AI-powered assistant for structured, multi-user collaboration for Markdown documents. 
                    Create or Upload, invite team members, ask the AI and start collaborating.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )    

    if app_users.Im_logged_in():

        
        filtered_docs = list(app_docs.filter_documents_for_user(app_users.user()))
        if filtered_docs:
            with st.expander("Your documents", expanded=True):
                selected_file = st.selectbox("Choose a document to continue editing", [""] + filtered_docs)
                if selected_file:
                    app_docs.set_active_document(selected_file)
                    st.switch_page("pages/10-write.py")

        with st.expander("Create a Document", expanded=not filtered_docs):
            app_docs.render_document_create()

        with st.expander("Upload a Document"):
            app_docs.render_document_upload()

        with st.expander("Documents Dashboard"): 
            # st.write("lala")  
            # st.selectbox("lolo", [1,2,3]) 
            app_docs.render_document_management()

        with st.expander("Change Password"): 
            app_users.render_change_my_password()

        if app_users.Im_admin():
            with st.expander("Admin"):
                app_users.render_user_management()
            
    else:
        st.subheader("Don't have an user yet?")
        app_users.render_create_user()

    # Check if no users exist in the YAML file
    if not app_users.load_users():
        app_users.render_create_admin()
            