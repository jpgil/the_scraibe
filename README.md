# the scrAIbe: AI-Assisted Writing for Teams

**the scrAIbe** is an AI-driven writing and collaboration platform designed to streamline the creation of lengthy, complex documents. Built entirely on Markdown, it integrates intelligent editing, dynamic document structuring, precise version tracking, and asynchronous multi-user collaboration.

## 🚀 Features

- **AI-Assisted Editing**: Context-aware editing options such as Expand, Shorten, Bulletize, Coherence Check, Writing Profile, and Equalize.
- **Dynamic Document Structure**: Pure Markdown-based structure with easy export to formats such as Word and PDF.
- **Smart Change Tracking & Version Control**: Unique section IDs and robust versioning to maintain history and enable rollbacks.
- **Asynchronous Multi-User Collaboration**: Section-locking system with granular read/write permissions.
- **Lightweight Deployment**: No installation required—clone and run.

---

## 🛠 Local Installation

To set up the environment locally, run:

```sh
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip wheel
pip install -r requirements.txt
```

To start the Streamlit dashboard:

```sh
python -m streamlit run src/dashboard.py
```

## GUI Deployment (Streamlit on Servers)

1. Ensure **Streamlit** is installed on your server.
2. Set up a virtual environment and install dependencies.
3. Run the Streamlit app on a server port:

```sh
streamlit run src/dashboard.py --server.port 8501
```

4. If deploying with **Streamlit Cloud**:
- Push the project to **GitHub**.
- Connect it to **Streamlit Cloud**.
- Set the main script (`src/dashboard.py`) and deploy.

---

## ✅ Running Tests

To execute all tests:

```sh
pytest
```

To run a specific test file:

```sh
pytest -s tests/test_locks.py
```

To run a specific test case:

```sh
pytest -s tests/test_locks.py -k test_01_lock_section
```

---

## 🤝 Contribute

We welcome contributions! Follow these steps:

1. **Fork the repository** on GitHub.
2. **Clone your fork**:

```sh
git clone https://github.com/yourusername/the-scrAIbe.git
cd the-scrAIbe
```

3. **Create a feature branch**:

```sh
git checkout -b feature-branch
```

4. **Make changes & commit**:

```sh
git add .
git commit -m "Added new feature"
```

5. **Push changes & submit a PR**: Then open a Pull Request on GitHub.

```sh
git push origin feature-branch
```

---

## 📜 License

This project is licensed under the **MIT License**. See the LICENSE file for details.

---

🚀 **the scrAIbe** is designed to accelerate document creation while maintaining clarity, traceability, and ease of use for both technical and non-technical stakeholders. Happy writing!