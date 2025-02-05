import os
import pytest
import yaml
import src.core as scraibe
from src.core.locks import lock_section, is_section_locked, unlock_section, check_all_locks

TEST_DOC = 'test_document.md'
TEST_SECTION = '20250203153000_1'
ANOTHER_SECTION = '20250203153000_2'
TEST_USER = 'jgil'
ANOTHER_USER = 'alice'

LOCK_FILE = f'locks/{TEST_DOC}/{TEST_DOC}.section_{TEST_SECTION}.lock'
ANOTHER_LOCK_FILE = f'locks/{TEST_DOC}/{TEST_DOC}.section_{ANOTHER_SECTION}.lock'

## 1 Lock the section
def test_01_lock_section():
    """Step 1: Lock a section and verify it is locked."""
    assert scraibe.lock_section(TEST_DOC, TEST_SECTION, TEST_USER) == True
    assert os.path.exists(LOCK_FILE)

    with open(LOCK_FILE, 'r', encoding='utf-8') as f:
        lock_data = yaml.safe_load(f)
        assert lock_data['user'] == TEST_USER

## 2 Check if the section is locked
def test_02_is_section_locked():
    """Step 2: Check that the section is correctly marked as locked."""
    assert is_section_locked(TEST_DOC, TEST_SECTION) == TEST_USER

## 3 Try locking the same section with another user
def test_03_lock_section_already_locked():
    """Step 3: Another user should NOT be able to lock the section."""
    assert scraibe.lock_section(TEST_DOC, TEST_SECTION, ANOTHER_USER) == False

## 4 Try unlocking with the wrong user
def test_04_unlock_section_wrong_user():
    """Step 4: The wrong user should NOT be able to unlock the section."""
    assert unlock_section(TEST_DOC, TEST_SECTION, ANOTHER_USER) == False
    assert os.path.exists(LOCK_FILE)

## 5 Unlock the section correctly
def test_05_unlock_section():
    """Step 5: The correct user should be able to unlock the section."""
    assert unlock_section(TEST_DOC, TEST_SECTION, TEST_USER) == True
    assert not os.path.exists(LOCK_FILE)

## 6 Check all locked sections for a document
def test_06_check_all_locks():
    """Step 6: Verify that check_all_locks correctly lists locked sections."""
    # Lock multiple sections
    assert scraibe.lock_section(TEST_DOC, TEST_SECTION, TEST_USER) == True
    assert scraibe.lock_section(TEST_DOC, ANOTHER_SECTION, ANOTHER_USER) == True

    locks = check_all_locks(TEST_DOC)
    
    assert locks == {
        TEST_SECTION: TEST_USER,
        ANOTHER_SECTION: ANOTHER_USER
    }

    # Cleanup
    assert unlock_section(TEST_DOC, TEST_SECTION, TEST_USER) == True
    assert unlock_section(TEST_DOC, ANOTHER_SECTION, ANOTHER_USER) == True

# Clean up after all tests
def teardown_module(module):
    """Cleans up any lock files after all tests."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    if os.path.exists(ANOTHER_LOCK_FILE):
        os.remove(ANOTHER_LOCK_FILE)
