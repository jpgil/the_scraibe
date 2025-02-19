# the scrAIbe

<p align="center">
  <img src="images/the_scribe-300.png" alt="the scrAIbe">
</p>

**the scrAIbe** is a prototype AI-driven writing and collaboration tool based on pure Markdown. It offers intelligent editing, dynamic structuring, version control, and asynchronous multi-user collaboration.

*Note that this is a prototype and not a production-ready application.*

## Key Features

- **AI-Assisted Editing**: Content Assessment, Coherence Check, and more.
- **Markdown-Based**: Pure Markdown structure with export options (Word, PDF).
- **Version Control**: Unique section IDs and rollback support (to be implemented)
- **Multi-User Collaboration**: Asynchronous editing with section locking.
- **Lightweight Setup**: Clone and run with Streamlit—no installation headaches.


## Getting Started

1. **Clone the repo**:

   git clone https://github.com/yourusername/the-scrAIbe.git
   cd the-scrAIbe

2. **Set up the environment:**

```sh
    python -m venv venv
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

3. **Write you LLM API key in the .env file:**
```sh
    cp .env-default .env
    nano .env
```
4. **Run the app:**

    streamlit run src/dashboard.py

## Running Tests
To execute all tests:

```sh
python -m pytest
```

To run a specific test file:

```sh
python -m pytest -s tests/test_locks.py
```

To run a specific test case:

```sh
python -m pytest -s tests/test_locks.py -k test_01_lock_section
```

## Contributing

1. Fork the repo and clone it locally.
2. Create a feature branch:
   ```git checkout -b feature-branch```
3. Commit your changes and open a PR.

## License
Licensed under the MIT License.









