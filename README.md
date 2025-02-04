# the scrAIbe

## Local install
    python -m venv venv
    source venv/bin/activate
    python -m pip install --upgrade pip wheel
    pip install -r requirements.txt

    pip install -e .

## Run tests

    # Run all
    pytest
    # Run one test
    pytest -s tests/test_locks.py
