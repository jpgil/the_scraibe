# Last changes for MVP

## Document Management
- [X] When creating new documents, add prompts to:
  - [X] Ask about the document's topic.
  - [X] Suggest initial content as a draft.
  - [X] Ask for the document’s purpose.
  - [X] Ask for the user's role in the document.
  - [X] Ask for the document's language.
- [ ] Fully implement file uploads.
- [ ] Infer title structure if the document is poorly formatted (e.g., when copying from a PDF).
- [X] Filter the document list to show only accessible documents.
- [X] Add a confirmation prompt when deleting a document.
## User Management
- [X] Remove the role selection.
- [X] Enable user creation for unregistered people.
- [X] Allow users to change their passwords.
  
## Write Page
- [ ] Implement the three AI tools and remove the "Your Role" option.
- [X] Verify the speed of searching blocked sections.
- [ ] In general AI tools, replace "Questions" with "Chat with the document."
- [X] Allow saving AI configuration along with the document’s metadata.
- [ ] Cleanup interface to show clearly the document area and the rest of interface. For example, render the document could have smaller font.

## AI Document Tools
- [ ] Infer headings and subheadings from the document.

# 📂 Repository Setup on GitHub
- [ ] Create a new GitHub repository (or use an existing one).
- [ ] Add a **README.md** with:
  - Project description.
  - Installation instructions.
  - Usage examples.
  - Contribution guidelines.
  - Contact information.
- [ ] Add a **LICENSE** file (MIT recommended).
- [X] Add a **.gitignore** file to exclude unnecessary files (e.g., `__pycache__/`, `.venv/`, `*.log`).
- [ ] Add a **requirements.txt** or **pyproject.toml** for dependencies.
- [ ] Configure **GitHub Actions** (optional, for CI/CD).
- [ ] Push the repository to GitHub.

# 🚀 Preparing for Streamlit Deployment
- [ ] Ensure `streamlit` is listed in `requirements.txt`.
- [ ] Create a **Streamlit app** (e.g., `app.py`).
- [ ] Test the app locally
  

# Tips and Tricks

- Custom CSS for containers: https://discuss.streamlit.io/t/applying-custom-css-to-manually-created-containers/33428/11
- Auth https://github.com/mkhorasani/Streamlit-Authenticator
- https://arnaudmiribel.github.io/streamlit-extras/extras/stylable_container/
- https://github.com/Mohamed-512/Extra-Streamlit-Components for Cookies
- https://github.com/null-jones/streamlit-plotly-events 
- https://github.com/Schluca/streamlit_tree_select
  

# Roadmap

## Document Management
- [ ] Add a "Last Edited" date to Your Documents.
- [ ] Implement the "Request Access" feature.

## User Management
- [ ] Upgrade to Streamlit-Authenticator

## AI Document Tools
- ...