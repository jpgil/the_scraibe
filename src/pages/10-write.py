import streamlit as st
from src.st_include import utils
import src.st_include.users as users
import src.st_include.documents as documents
import src.core as scraibe


if __name__ == "__main__":
    utils.sidebar(__file__)
    
    if not users.Im_logged_in():
        utils.notify("Login to see documents", switch="ui.py")
        st.stop()
                
    current_user = st.session_state.get("username")
    filtered_docs = list(documents.filter_documents_for_user(current_user))
    
    if not filtered_docs:
        utils.notify("You should create your first document", switch="ui.py")

    if st.session_state.get("document_file") not in filtered_docs:
        st.info("Select a document to write")
        st.stop()

    # All good, let's show it
    content = scraibe.load_document_nolabels(st.session_state["document_file"])

    cols = st.columns([5,1])
    with cols[0]:
        with st.container(border=True):
            st.markdown(content)
    with cols[1]:
        st.button("edit", use_container_width=True)
        st.button("delete", use_container_width=True)
        st.button("history", use_container_width=True)
    st.button("add section", use_container_width=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar.container():
        # Build the HTML for all messages
        chat_html = '<div class="fixed-height">'
        for message in st.session_state.messages:
            # Customize the HTML as needed; this is a simple example.
            chat_html += f"<p><strong>{message['role']}:</strong> {message['content']}</p>"
        chat_html += '</div>'

        # Render the fixed container with the chat HTML
        st.markdown(
            """
            <style>
            .fixed-height {
                height: 300px;
                overflow: auto;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(chat_html, unsafe_allow_html=True)

        if user_input := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            # Here you can add the logic to handle the user input and generate a response
            # For example, you can call a function to get a response from a chatbot model
            response = "This is a placeholder response."
            st.session_state.messages.append({"role": "bot", "content": response})
            st.rerun()