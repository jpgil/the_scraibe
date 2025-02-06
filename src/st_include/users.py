import streamlit as st
import yaml
import os
import hashlib
import pandas as pd
import time
from src.st_include import utils
from datetime import datetime

# Load users from YAML
USER_DB = "users.yaml"


def load_users():
    """Load user data from YAML file."""
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as file:
            return yaml.safe_load(file) or {}
    return {}


def save_users(users):
    """Save user data to YAML file."""
    with open(USER_DB, "w") as file:
        yaml.dump(users, file)
    return True


def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def delete_user(username):
    """Delete a user from the system."""
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return True
        utils.notify(f"User {username} deleted.", switch="ui.py")  # TODO: move outside
    else:
        return False
        st.error("User not found!")  # TODO: move outside

def add_user(username, password, role="viewer"):
    """Add a new user to the system (Admin only)."""
    users = load_users()
    
    if username in users:
        st.error("User already exists!")  # TODO: move outside
        return False

    users[username] = {
        "password": hash_password(password),
        "role": role,
        "last_login": None
    }
    
    save_users(users)
    utils.notify(f"User {username} created successfully.")

def update_role(username, new_role):
    """Update a user's role."""
    users = load_users()
    if username in users:
        users[username]["role"] = new_role
        save_users(users)
        utils.notify(f"Role updated to {new_role} for {username}")
    else:
        st.error("User not found!")  # TODO: move outside

def update_password(username, new_password):
    """Update a user's password."""
    users = load_users()
    if username in users:
        users[username]["password"] = hash_password(new_password)
        save_users(users)
        utils.notify(f"Password updated for {username}")
    else:
        st.error("User not found!")  # TODO: move outside


def reset_password(username):
    """Reset user password (Admin only or self)."""
    users = load_users()
    
    if username not in users:
        st.error("User does not exist!")  # TODO: move outside
        return False
    
    new_password = st.text_input("Enter new password", type="password")  # TODO: move outside
    if st.button("Confirm Reset"):  # TODO: move outside
        users[username]["password"] = hash_password(new_password)
        save_users(users)
        st.success("Password updated successfully!")  # TODO: move outside
        return True



def do_login(username, password):
    """Authenticate user and start a session."""
    users = load_users()

    if username not in users or users[username]["password"] != hash_password(password):
        st.error("Invalid username or password!") 

    else:
        # Store session state
        st.session_state["logged_in"] = True  # TODO: move outside
        st.session_state["username"] = username  # TODO: move outside
        st.session_state["role"] = users[username]["role"]  # TODO: move outside
        
        users[username]["last_login"] = datetime.now()  # Placeholder for real timestamp
        save_users(users)

        utils.notify(f"Welcome, {username}!")
        return True

def Im_admin():
    return "role" in st.session_state and st.session_state["role"] == "admin"

def Im_logged_in():
    return "logged_in" in st.session_state

def render_user_loggedin():
    if st.button(f"Logout {st.session_state['username']}"):
        st.session_state.clear()  # TODO: move outside
        utils.notify("Logged out successfully!")

def render_user_loggedout():
    with st.form(key="login_form", border=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    
    if submit:
        do_login(username, password)

            

def render_create_admin(user):
    st.warning("No users found. Please create an initial admin user.")
    username = st.text_input("New Username", key="newuser2")
    password = st.text_input("New Password", type="password", key="newpass2")
    role = "admin"

    if st.button("Create Admin User"):
        add_user(username, password, role)
        do_login(username, password)
        # st.rerun()

def render_user_management():
    """Admin panel for managing users."""
    if st.session_state.get("role") != "admin":
        st.warning("You need admin access to manage users.")
        return
    
    st.header("Admin Management")

    tab = st.tabs(["User List", "User Management", "Add User"])
    
    with tab[0]:

        users = load_users()
        
        if not users:
            st.write("No users found.")
            return

        # Convert user data to a DataFrame
        df = pd.DataFrame.from_dict(users, orient="index")
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Username", "role": "Role", "last_login": "Last Login"}, inplace=True)
        
        user_list = df['Username'].to_list()

        st.write("Existing users")
        st.dataframe(df, hide_index=True, column_order=["Username", "Last Login", "Role"], use_container_width=True)
        
        
    with tab[1]:
        selected_user = st.selectbox("Selected user", ['[None]'] + user_list)

        if selected_user != "[None]":
            
            selected_user_data = users[selected_user]
            # st.write(selected_user_data)

            col1, col2, _ = st.columns([3, 3, 3])
            with col1:
                new_role = st.selectbox(
                    "Role", 
                    ["viewer", "editor", "admin"],
                    label_visibility='collapsed',
                    index=["viewer", "editor", "admin"].index(selected_user_data["role"])
                )
            with col2:
                if st.button("Update Role"):
                    update_role(selected_user, new_role)

            col1, col2, _ = st.columns([3, 3, 3])
            with col1:
                new_password = st.text_input(
                    "New Password", 
                    label_visibility='collapsed',
                    type="password"
                )
            with col2:
                if st.button("Update Password"):
                    update_password(selected_user, new_password)

            col1, col2, _ = st.columns([3, 3, 3])
            with col1:
                confirm = st.selectbox(
                    "Confirm deletion", 
                    ["No", "Yes"],
                    label_visibility='collapsed',
                )
            with col2:
                if st.button("Delete User") and confirm == "Yes":
                    if delete_user(selected_user):
                        utils.notify(f"User {selected_user} deleted.", switch="ui.py")
                    else:
                        st.error("User not found!")

    with tab[2]:
        st.header("Add User")

        # Create new user
        col1, col2, col3 = st.columns(3)
        with col1:
            username = st.text_input("New Username", key="new_username")
        with col2:
            password = st.text_input("New Password", type="password", key="new_password")
        with col3:
            role = st.selectbox("Role", ["viewer", "editor", "admin"], key="new_role")
        
        if st.button("Add User"):
            if username and password:
                users = load_users()
                if username not in users:
                    users[username] = {
                        "password": hash_password(password),
                        "role": role,
                        "last_login": None
                    }
                    if save_users(users):
                        utils.notify(f"User {username} added successfully!", switch="ui.py")
                    else:
                        st.error("Something bad happened")
                        
                else:
                    st.error("User already exists.")
            else:
                st.error("Username and password are required.")
