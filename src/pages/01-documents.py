import streamlit as st
import yaml
import os
from datetime import datetime
import pandas as pd
from src.st_include import utils
import src.st_include.users as users
import src.core as scraibe

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

def add_document(filename, creator):
    """Add a new document. The creator is stored as the owner with fixed rights."""
    docs = load_documents()
    if filename in docs["documents"]:
        st.error("Document already exists!")
        return False

    docs["documents"][filename] = {
        "creator": creator,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "users": [{"name": creator, "permission": "creator", "display_name": creator}]
    }
    
    content = f"""
# {filename.replace(".md", "")}
Your content will be here
"""
    content = scraibe.add_section_markers(content)
    scraibe.save_document(filename, content)
    save_documents(docs)
    utils.notify(f"Document {filename} created successfully!")
    return True

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
    utils.notify(f"Permissions updated for {username} in document {filename}")
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
    utils.notify(f"User {username} removed from document {filename}")
    return True

def filter_documents_for_user(username):
    """Return a dictionary of documents for which the given username is listed."""
    all_docs = load_documents()["documents"]
    return {doc: meta for doc, meta in all_docs.items() if any(u["name"] == username for u in meta.get("users", []))}

def render_document_list():
    """Display a table with existing documents and their metadata."""
    docs = load_documents()["documents"]
    if not docs:
        st.info("No documents available.")
        return

    rows = []
    for doc, meta in docs.items():
        user_list_str = ", ".join([f"{u['display_name']}({u['permission']})" for u in meta.get("users", [])])
        rows.append({"Document": doc, "Creator": meta.get("creator", ""), "Created At": meta.get("created_at", ""), "Users": user_list_str})

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True)

def render_grant_permissions(doc_to_manage, doc_meta, key_prefix, button_label):
    """Render UI to grant permissions for adding a new user."""
    all_users = users.load_users()
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
    for entry in doc_meta.get("users", []):
        if entry["name"] == doc_meta.get("creator"):
            st.write(f"**Creator: {entry['display_name']} ({entry['name']})**")
            continue

        cols = st.columns([3, 3, 3, 3])
        with cols[0]:
            new_permission = st.selectbox(label=f"Permission for {entry['name']}", options=["viewer", "editor", "none"], label_visibility="collapsed", index=(["viewer", "editor", "none"].index(entry["permission"]) if entry["permission"] in ["viewer", "editor", "none"] else 0), key=f"perm_{entry['name']}")
        with cols[1]:
            new_display = st.text_input(label=f"Display name for {entry['name']}", label_visibility="collapsed", value=entry.get("display_name", entry["name"]), key=f"disp_{entry['name']}")
        with cols[2]:
            if st.button(label=f"Update {entry['name']}", key=f"update_{entry['name']}"):
                update_document_permission_for_user(doc_to_manage, entry["name"], new_permission, new_display)
        with cols[3]:
            if st.button(label=f"Remove {entry['name']}", key=f"remove_{entry['name']}"):
                remove_user_permission(doc_to_manage, entry["name"])

    st.markdown("#### Grant Permissions")
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

    st.markdown("#### Grant Permissions")
    render_grant_permissions(doc_to_manage=doc_to_manage, doc_meta=doc_meta, key_prefix="editor", button_label="Add User as Editor")

def render_document_management():
    """Render the document management dashboard."""
    st.header("Document Management")
    tabs = st.tabs(["Document List", "Add Document", "Manage Permissions", "Delete Document"])

    # Tab 1: Document List
    with tabs[0]:
        st.subheader("Existing Documents")
        render_document_list()

    # Tab 2: Add New Document
    with tabs[1]:
        st.subheader("Add New Document")
        filename = st.text_input(label="Document Filename (e.g., document01.md)", key="doc_filename")
        creator = st.session_state.get("username", "")
        if st.button(label="Create Document"):
            if filename and creator:
                add_document(filename, creator)
            else:
                st.error("Filename and creator are required.")

    # Tab 3: Manage Permissions
    with tabs[2]:
        st.subheader("Manage Document Permissions")
        current_user = st.session_state.get("username")
        filtered_docs = filter_documents_for_user(current_user)
        if not filtered_docs:
            st.info("No documents to manage.")
        else:
            doc_to_manage = st.selectbox(label="Select Document", options=list(filtered_docs.keys()), key="doc_manage")
            doc_meta = filtered_docs[doc_to_manage]
            creator = doc_meta.get("creator")
            st.write(f"Document created by: **{creator}**")
            st.markdown("#### Current Permissions")
            for entry in doc_meta.get("users", []):
                st.write(f"- {entry['display_name']} ({entry['name']}): {entry['permission']}")

            if current_user == creator:
                render_manage_permissions_for_creator(doc_to_manage=doc_to_manage, doc_meta=doc_meta)
            else:
                if any(u["name"] == current_user and u["permission"] in ["editor", "creator"] for u in doc_meta.get("users", [])):
                    render_manage_permissions_for_editor(doc_to_manage=doc_to_manage, doc_meta=doc_meta, current_user=current_user)
                else:
                    st.error("You do not have permissions to manage this document.")

    # Tab 4: Delete Document
    with tabs[3]:
        st.subheader("Delete Document")
        current_user = st.session_state.get("username")
        filtered_docs = filter_documents_for_user(current_user)
        if not filtered_docs:
            st.info("No documents available to delete.")
        else:
            doc_to_delete = st.selectbox(label="Select Document to Delete", options=list(filtered_docs.keys()), key="doc_delete")
            if st.session_state.get("username") == filtered_docs[doc_to_delete]["creator"]:
                if st.button(label="Delete Document"):
                    docs = load_documents()["documents"]
                    del docs[doc_to_delete]
                    save_documents({"documents": docs})
                    utils.notify(f"Document {doc_to_delete} deleted successfully!")
            else:
                st.error("Only the creator can delete the document.")

if __name__ == "__main__":
    utils.sidebar(__file__)
    if not users.Im_logged_in():
        utils.notify("Login to see documents", switch="ui.py")
    st.title("Documents Dashboard")
    render_document_management()
