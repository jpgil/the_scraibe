# Last changes for MVP

## Document Management
- [ ] Add a "Last Edited" date to documents.
- [ ] When creating new documents, add prompts to:
  - [ ] Ask about the document's topic.
  - [ ] Suggest initial content as a draft.
  - [ ] Ask for the document’s purpose.
  - [ ] Ask for the user's role in the document.
  - [ ] Ask for the document's language.
- [ ] Fully implement file uploads.
- [ ] Infer title structure if the document is poorly formatted (e.g., when copying from a PDF).
- [ ] Filter the document list to show only accessible documents.
- [ ] Implement the "Request Access" feature.
- [ ] Add a confirmation prompt when deleting a document.
## User Management
- [ ] When adding a new user:
  - [ ] Remove the role selection.
  - [ ] Add fields for email and real name.
  - [ ] Enable user creation for unregistered people.
- [ ] Allow users to change their passwords.
  
## Write Page
- [ ] Implement the three AI tools and remove the "Your Role" option.
- [ ] Verify the speed of searching blocked sections.
- [ ] In general AI tools, replace "Questions" with "Chat with the document."
- [ ] Allow saving AI configuration along with the document’s metadata.

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