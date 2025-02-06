import streamlit as st
import src.st_include.users as users
import src.st_include.utils as utils


# UI Setup
utils.sidebar(__file__)
st.title("the scrAIbe")

if not users.Im_logged_in():
    st.image("images/the_scribe.png", width=300)

if users.Im_admin():
    users.render_user_management()

# Check if no users exist in the YAML file
if not users.load_users():
    users.render_create_admin()
        