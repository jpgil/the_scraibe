
import subprocess

TEST_DOC = 'test_document.md'
TEST_SECTION = '20250203153000_1'
TEST_USER = 'jgil'
ANOTHER_USER = 'alice'

def test_01_lock_section():
    """Step 1: Lock a section from CLI."""
    result = subprocess.run(['python', 'src/cli.py', 'lock', TEST_DOC, TEST_SECTION, TEST_USER], capture_output=True, text=True)
    assert f'Section {TEST_SECTION} locked by {TEST_USER}.' in result.stdout

def test_02_check_section_locked():
    """Step 2: Verify section is locked."""
    result = subprocess.run(['python', 'src/cli.py', 'check-lock', TEST_DOC, TEST_SECTION], capture_output=True, text=True)
    assert f'Section {TEST_SECTION} is locked by {TEST_USER}.' in result.stdout

def test_03_lock_section_already_locked():
    """Step 3: Attempt to lock the section with another user."""
    result = subprocess.run(['python', 'src/cli.py', 'lock', TEST_DOC, TEST_SECTION, ANOTHER_USER], capture_output=True, text=True)
    assert f'Error: Section {TEST_SECTION} is already locked by another user.' in result.stdout

def test_04_unlock_section_wrong_user():
    """Step 4: Attempt to unlock with a different user."""
    result = subprocess.run(['python', 'src/cli.py', 'unlock', TEST_DOC, TEST_SECTION, ANOTHER_USER], capture_output=True, text=True)
    assert f'Error: {ANOTHER_USER} does not have permission to unlock section {TEST_SECTION}.' in result.stdout

def test_05_unlock_section_correct_user():
    """Step 5: Unlock with the correct user."""
    result = subprocess.run(['python', 'src/cli.py', 'unlock', TEST_DOC, TEST_SECTION, TEST_USER], capture_output=True, text=True)
    assert f'Section {TEST_SECTION} unlocked by {TEST_USER}.' in result.stdout

