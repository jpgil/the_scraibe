import streamlit as st
import yaml
import os
from datetime import datetime
import pandas as pd
from src.st_include import app_utils
from src.st_include import app_users
import src.core as scraibe

#
# TODO: Split pure docs functions and streamlit frontend functions


# YAML file for document metadata
DOC_DB = "documents.yaml"

def load_documents():
    """Load document metadata from YAML file."""
    if os.path.exists(DOC_DB):
        with open(DOC_DB, "r") as file:
            data = yaml.safe_load(file) or {}
            if "documents" not in data:
                data["documents"] = {}
            return data
    return {"documents": {}}

def save_documents(documents):
    """Save document metadata to YAML file."""
    with open(DOC_DB, "w") as file:
        yaml.dump(documents, file)
    return True

def add_document(filename, creator, lang=None, purpose=None, role=None, document_content=""):
    """Add a new document. The creator is stored as the owner with fixed rights."""
    docs = load_documents()
    if not filename.endswith(".md"):
        filename += ".md"

    if filename in docs["documents"]:
        st.error("Document already exists!")
        return False
    

    docs["documents"][filename] = {
        "creator": creator,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "users": [{"name": creator, "permission": "creator", "display_name": creator}]
    }
    docs["documents"][filename]["lang"] = lang
    docs["documents"][filename]["purpose"] = purpose
    docs["documents"][filename]["role"] = role
    
    if document_content == "":
        scraibe.llm.user_role = role
        scraibe.llm.purpose = purpose
        scraibe.llm.lang = lang
        content = scraibe.llm.create_content(filename.replace('.md', ''))
    #     if content == "":
    #     content = f"""
    # # {filename.replace(".md", "")}
    # Your content will be here
    # """
    else:
        content = document_content
        if not content.startswith("#"):
            content = f"# {filename.replace('.md', '')}\n\n" + content

    content = scraibe.add_section_markers(content)
    scraibe.save_document(filename, content)
    save_documents(docs)

    return os.path.basename(scraibe.get_filename_path(filename))

def update_document_permission_for_user(filename, username, permission, display_name=None):
    """Update the permission (and optionally display name) for a given user in a document."""
    docs = load_documents()
    if filename not in docs["documents"]:
        st.error("Document not found!")
        return False

    users_list = docs["documents"][filename].get("users", [])
    found = False

    for entry in users_list:
        if entry["name"] == username:
            if entry["permission"] == "creator":
                st.error("Cannot modify creator's permissions.")
                return False
            entry["permission"] = permission
            if display_name:
                entry["display_name"] = display_name
            found = True
            break

    if not found and permission != "none":
        new_entry = {"name": username, "permission": permission, "display_name": display_name or username}
        users_list.append(new_entry)

    docs["documents"][filename]["users"] = users_list
    save_documents(docs)
    app_utils.notify(f"Permissions updated for {username} in document {filename}")
    return True

def remove_user_permission(filename, username):
    """Remove a user from a document’s permissions (cannot remove the creator)."""
    docs = load_documents()
    if filename not in docs["documents"]:
        st.error("Document not found!")
        return False

    users_list = docs["documents"][filename].get("users", [])
    new_list = []

    for entry in users_list:
        if entry["name"] == username:
            if entry["permission"] == "creator":
                st.error("Cannot remove the creator.")
                return False
            continue
        new_list.append(entry)

    docs["documents"][filename]["users"] = new_list
    save_documents(docs)
    app_utils.notify(f"User {username} removed from document {filename}")
    return True

# @st.cache_data(ttl=5)
def filter_documents_for_user(username, remove_cache=False):
    """Return a dictionary of documents for which the given username is listed."""
    all_docs = load_documents()["documents"]
    return {
        doc: meta for doc, meta in all_docs.items() 
        if any(u["name"] == username for u in meta.get("users", []))
        }

#
# File properties & checks
# ---------------
#


def set_active_document(document):
    st.session_state["document_file"] = document
    st.session_state['last_active_id'] = ""
    set_editing_section_id(False, False)
    set_selected_section_id(False, False)
def active_document():
    return st.session_state["document_file"]

def set_editing_section_id(section_id, rerun=True):
    #TODO: check that previous section has been saved
    st.session_state['editing_section_id'] = section_id
    if rerun:
        st.rerun()
    
def editing_section_id():
    return st.session_state.get('editing_section_id', '')

def set_selected_section_id(section_id, rerun=True):
    st.session_state['selected_section_id'] = section_id
    if rerun:
        st.rerun()

def selected_section_id():
    return st.session_state.get('selected_section_id', '')


#
# Renders for Streamlit
# ---------------------
#
def render_document_list():
    """Display a table with existing documents and their metadata."""
    allowed_docs = filter_documents_for_user(app_users.user())
    docs = load_documents()["documents"] 
    
    if not docs:
        st.info("No documents available.")
        return

    rows = []
    for doc, meta in docs.items():
        if doc in allowed_docs:
            user_list_str = ", ".join([f"{u['display_name']}({u['permission']})" for u in meta.get("users", [])])
            rows.append({"Document": doc, "Creator": meta.get("creator", ""), "Created At": meta.get("created_at", ""), "Users": user_list_str})

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True)

def render_grant_permissions(doc_to_manage, doc_meta, key_prefix, button_label):
    """Render UI to grant permissions for adding a new user."""
    all_users = app_users.load_users()
    current_doc_users = [u["name"] for u in doc_meta.get("users", [])]
    available_users = [u for u in all_users.keys() if u not in current_doc_users]

    if available_users:
        col1, col2, col3 = st.columns([3, 3, 3])
        with col1:
            new_user_permission = st.selectbox(label="Permission", options=["viewer", "editor"], key=f"{key_prefix}_perm")
        with col2:
            new_user = st.selectbox(label="Select new user to add", options=available_users, key=f"{key_prefix}_user")
        with col3:
            new_user_display = st.text_input(label="Display Name", value=new_user, key=f"{key_prefix}_disp")
        if st.button(label=button_label, key=f"{key_prefix}_btn"):
            update_document_permission_for_user(doc_to_manage, new_user, new_user_permission, new_user_display)
    else:
        st.info("No available users to add.")

def render_manage_permissions_for_creator(doc_to_manage, doc_meta):
    """Render permission management UI for the document creator."""
    st.info("You are the creator. You can update permissions for any user.")
    st.markdown("#### Edit Permissions")
    for entry in doc_meta.get("users", []):
        disabled_label = entry["name"] == doc_meta.get("creator")
        cols = st.columns([3, 3, 3, 3])
        with cols[0]:
            new_permission = st.selectbox(
                label=f"Permission for {entry['name']}",
                options=["viewer", "editor", "none"] if not disabled_label else ["CREATOR"],
                label_visibility="collapsed",
                disabled=disabled_label,
                index=(["viewer", "editor", "none"].index(entry["permission"]) if entry["permission"] in ["viewer", "editor", "none"] else 0),
                key=f"perm_{entry['name']}"
            )
            with cols[1]:
                new_display = st.text_input(
                label=f"Display name for {entry['name']}",
                label_visibility="collapsed",
                disabled=disabled_label,
                value=entry.get("display_name", entry["name"]),
                key=f"disp_{entry['name']}"
                )
            with cols[2]:
                if not disabled_label and st.button(
                    label=f"Update {entry['name']}",
                    key=f"update_{entry['name']}"
                ):
                    update_document_permission_for_user(doc_to_manage, entry["name"], new_permission, new_display)
            with cols[3]:
                if not disabled_label and st.button(
                label=f"Remove {entry['name']}",
                key=f"remove_{entry['name']}"
                ):
                    remove_user_permission(doc_to_manage, entry["name"])

    st.markdown("#### Grant New Permissions")
    render_grant_permissions(doc_to_manage=doc_to_manage, doc_meta=doc_meta, key_prefix="creator", button_label="Add User")

def render_manage_permissions_for_editor(doc_to_manage, doc_meta, current_user):
    """Render permission management UI for an editor (non-creator)."""
    st.info("You are an editor. You can update your own display name and add new users.")
    for entry in doc_meta.get("users", []):
        if entry["name"] == current_user:
            new_display = st.text_input(label="Your Display Name", value=entry.get("display_name", current_user), key="self_disp")
            if st.button(label="Update My Name", key="update_self"):
                update_document_permission_for_user(doc_to_manage, current_user, entry["permission"], new_display)
            break

    st.markdown("#### Grant New Permissions")
    render_grant_permissions(doc_to_manage=doc_to_manage, doc_meta=doc_meta, key_prefix="editor", button_label="Add User as Editor")

def render_document_upload():
    st.subheader("Upload Document")
    filename = st.file_uploader(label="Document Filename (e.g., document01.md)", key="upload_doc_filename")
    creator = st.session_state.get("username", "")
    if st.button(label="Upload Document"):
        if filename and creator:
            st.error("Not implemented yet")
            # if documents.add_document(filename, creator):
            #     utils.notify(f"Document {filename} created successfully!", switch="pages/01-documents.py")
        else:
            st.error("Filename and creator are required.")

def render_document_create(*args, **kwargs):
    st.subheader("Create New Document")

    with st.form(key=f'document_create', border=False):
        filename = st.text_input(label="Document Filename / Title", key="doc_filename", help=".md will be added at the end")
        creator = st.session_state.get("username", "")
        
        langs = ["Inferred from the document", "English", "Español", "Français", "Deutsch"]
        lang = st.selectbox("[optional] Document language", langs)

        purpose = st.text_input("[optional] Main purpose of this document", value="Inferred from the document", help="""
    Describe in detail what is the main goal of this document. For example:

    - This is a technical document that propose team standards to implement CI/CD
    - This is the README of a git repository containing a website based on streamlit to solve problem X
        """)
        
        my_role = st.text_input("[optional] Your role in this document", value="Expert in the topic of the document", help=""" 
    Describe any specific role you can have in this document. E.g:
    
    - A seasoned DevOps engineer 
    - The manager who reviews the content
    - Specialist in documentation formalisms 
        """)
        
        document_content = st.text_area("[optional] Initial content of the document", value="", height=150, help=""" 
If no content is provided, the scrAIbe will propose an initial content based on the document name and purpose.
        """)
        
        if st.form_submit_button("Create Document"):
            if filename and creator:
                document_file = add_document(filename, creator, lang, purpose, my_role, document_content)
                if document_file:
                    set_active_document(document_file)
                    app_utils.notify(f"Document {document_file} created successfully!", switch="pages/10-write.py")
            else:
                st.error("Filename and creator are required.")
            
def render_document_management():
    """Render the document management dashboard."""
    # current_user = st.session_state["username"]
    user_role    = st.session_state["role"]
    current_user = app_users.user()
    filtered_docs = filter_documents_for_user(current_user)

    if user_role in ["editor", "admin"]:
        # tab_list = ["Document List", "Add Document", "Manage Permissions", "Delete Document"]
        # tab_list = ["Document List", "Request access", "Manage Permissions", "Delete Document"]
        tab_list = ["Document List", "Manage Permissions", "Delete Document"]
    else:
        tab_list = ["Document List"]
    tabs = st.tabs(tab_list)

    # Tab 1: Document List
    if "Document List" in tab_list:
        with tabs[tab_list.index("Document List")]:
            # st.header("Existing Documents")
            render_document_list()

    # # Tab 2: Add New Document
    # if "Add Document" in tab_list:
    #     with tabs[tab_list.index("Add Document")]:
    #         render_document_upload()
    #         render_document_create()

    # Tab 3: Manage Permissions
    if "Manage Permissions" in tab_list:
        with tabs[tab_list.index("Manage Permissions")]:
            # st.header("Manage Document Permissions")
            if not filtered_docs:
                st.info("No documents to manage.")
            else:
                doc_to_manage = st.selectbox(label="Select Document", options=[""]+list(filtered_docs.keys()), key="doc_manage")
                if doc_to_manage:
                    st.markdown("-----")
                    doc_meta = filtered_docs[doc_to_manage]
                    # table_users = []
                    # for entry in doc_meta.get("users", []):
                    #     table_users.append({"username": entry['display_name'], "role": entry['permission']})
                    # df = pd.DataFrame(table_users)
                    # st.dataframe(df, column_config={"username": "Username", "role": "Role"}, hide_index=True)
                    
                    # st.write(doc_meta.get("users", []))
                    
                    creator = doc_meta.get("creator")
                    if current_user == creator:
                        render_manage_permissions_for_creator(doc_to_manage=doc_to_manage, doc_meta=doc_meta)
                    else:
                        if any(u["name"] == current_user and u["permission"] in ["editor", "creator"] for u in doc_meta.get("users", [])):
                            render_manage_permissions_for_editor(doc_to_manage=doc_to_manage, doc_meta=doc_meta, current_user=current_user)
                        else:
                            st.error("You do not have permissions to manage this document.")

    # Tab 4: Delete Document 
    if "Delete Document" in tab_list:
        with tabs[tab_list.index("Delete Document")]:
            # st.header("Delete Document")
            current_user = app_users.user()
            filtered_docs = filter_documents_for_user(current_user)
            if not filtered_docs:
                st.info("No documents available to delete.")
            else:
                doc_to_delete = st.selectbox(label="Select Document to Delete", options=[""]+list(filtered_docs.keys()), key="doc_delete")
                if doc_to_delete:
                    if current_user == filtered_docs[doc_to_delete]["creator"]:
                        if st.button(label="Delete Document"):
                            def delete_doc():
                                docs = load_documents()
                                del docs["documents"][doc_to_delete]
                                save_documents(docs)
                                scraibe.delete_document(doc_to_delete)
                            app_utils.confirm_action("Delete this document?", delete_doc)
                    else:
                        st.error("Only the creator can delete the document.")

    # if "Request access" in tab_list:
    #     with tabs[tab_list.index("Request access")]:
    #         st.warning("Feature not implemented yet")

    #         if not filtered_docs:
    #             st.info("No documents to manage.")
    #         else:
    #             col1, col2 = st.columns([3,1])
    #             with col1:
    #                 doc_to_manage = st.selectbox("Request access to", [""] + list(filtered_docs.keys()), key="doc_access")
    #             with col2:
    #                 role = st.selectbox("As role", ["", "viewer", "editor"])
                
    #             if doc_to_manage and role:
    #                 if filtered_docs[doc_to_manage].get('creator') == st.session_state['username']:
    #                     st.info
    #                 if st.button(f"Request access to {filtered_docs[doc_to_manage].get('creator')}"):
    #                     st.error("As I said, not implement yet!")
