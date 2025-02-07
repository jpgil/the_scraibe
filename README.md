# the scrAIbe
{Write here the description. Use the standards of GITHUB }

## Local install
    python -m venv venv
    source venv/bin/activate
    python -m pip install --upgrade pip wheel
    pip install -r requirements.txt

    python -m streamlit run src/dashboard.py

## GUI Deployment
{Instructions for streamlit in servers}


## Run tests
    # Run all
    pytest

    # Run one testfile
    pytest -s tests/test_locks.py

    # Run one testcase
    pytest -s tests/test_locks.py -k test_01_lock_section

## Contribute

## Licence MIT
{write here}