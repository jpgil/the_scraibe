import os
import re
import subprocess
import pytest
import src.core as scraibe
import time

TEST_DOC = "documents/test_document.md"
ANOTHER_SECTION = "20250203153000_2"
TEST_USER = "gammow"
ANOTHER_USER = "alice"
REVIEW_USER = "bob"
VERSION_TIMESTAMP = "20250204120000"

@pytest.fixture(scope="module", autouse=True)
def setup_and_cleanup():
    """Ensures the test document is created and cleaned up."""
    # time.sleep(0.1)
    os.makedirs("documents", exist_ok=True)
    os.makedirs("versions", exist_ok=True)
    
    content = "# Test Document\n\nThis is a test."
    content = scraibe.add_section_markers(content)

    with open(TEST_DOC, "w", encoding="utf-8") as f:
        f.write(content)
    yield

    if os.path.exists(TEST_DOC):
        os.remove(TEST_DOC)
    # Remove versions
    version_files = [f for f in os.listdir('versions') if f.startswith(f"{os.path.basename(TEST_DOC)}.section_")]
    for vf in version_files:
        os.remove(os.path.join('versions', vf))
    # Remove locks
    lock_files = [f for f in os.listdir('locks') if f.startswith(f"{os.path.basename(TEST_DOC)}.section_")]
    for lf in lock_files:
        os.remove(os.path.join('locks', lf))
    


# 01. Basic Workflow: Label Sections
def test_01_label_sections():
    result = subprocess.run(["python", "src/cli.py", "-v", "label-sections", TEST_DOC], capture_output=True, text=True)
    assert "has been labeled" in result.stdout


# 02. Lock, Edit, and Unlock a Section
def test_02_lock_edit_unlock_section():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]

    subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, section, TEST_USER], check=True)
    lock_status = subprocess.run(["python", "src/cli.py", "-v", "check-lock", TEST_DOC, section], capture_output=True, text=True)
    assert TEST_USER in lock_status.stdout

    subprocess.run(["python", "src/cli.py", "-v", "unlock", TEST_DOC, section, TEST_USER], check=True)


# 03. Prevent Concurrent Editing
def test_03_prevent_concurrent_editing():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]

    subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, section, TEST_USER], check=True)
    result = subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, section, ANOTHER_USER], capture_output=True, text=True)
    assert "is already locked" in result.stdout

    subprocess.run(["python", "src/cli.py", "-v", "unlock", TEST_DOC, section, TEST_USER], check=True)


# 04. Save a New Version of a Section
def test_04_save_new_version():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]

    subprocess.run(["python", "src/cli.py", "-v", "save-section", TEST_DOC, section, TEST_USER, "Updated content here."], check=True)
    result = subprocess.run(["python", "src/cli.py", "-v", "list-versions", TEST_DOC, section], capture_output=True, text=True)
    assert "Previous versions of section" in result.stdout


# 05. Rollback to a Previous Version
def test_05_rollback_section():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]
    timestamp = scraibe.save_section(TEST_DOC, section, "user1", "content1")

    scraibe.save_section(TEST_DOC, section, "user2", "content2")
    scraibe.save_section(TEST_DOC, section, "user3", "content3")

    result = subprocess.run(["python", "src/cli.py", "-v", "rollback-section", TEST_DOC, section, timestamp, "user1"], capture_output=True, text=True)
    assert "rolled back to version" in result.stdout


# 06. Full Editing Workflow
def test_06_full_editing_workflow():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]

    subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, section, TEST_USER], check=True)
    subprocess.run(["python", "src/cli.py", "-v", "save-section", TEST_DOC, section, TEST_USER, "This is a revised version."], check=True)
    subprocess.run(["python", "src/cli.py", "-v", "unlock", TEST_DOC, section, TEST_USER], check=True)

    result = subprocess.run(["python", "src/cli.py", "-v", "list-versions", TEST_DOC, section], capture_output=True, text=True)
    assert "Previous versions of section" in result.stdout


# 07. Multi-User Collaboration Workflow
def test_07_multi_user_collaboration():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]
    
    subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, section, ANOTHER_USER], check=True)
    alice_version = subprocess.run(["python", "src/cli.py", "-v", "save-section", TEST_DOC, section, ANOTHER_USER, "Alice's contribution."], capture_output=True, text=True).stdout.strip().split()[-1]
    subprocess.run(["python", "src/cli.py", "-v", "unlock", TEST_DOC, section, ANOTHER_USER], check=True)

    subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, section, REVIEW_USER], check=True)
    bob_version = subprocess.run(["python", "src/cli.py", "-v", "save-section", TEST_DOC, section, REVIEW_USER, "Bob reviewed and improved."], capture_output=True, text=True).stdout.strip().split()[-1]
    subprocess.run(["python", "src/cli.py", "-v", "unlock", TEST_DOC, section, REVIEW_USER], check=True)

    result = subprocess.run(["python", "src/cli.py", "-v", "list-versions", TEST_DOC, section], capture_output=True, text=True).stdout
    assert alice_version in result
    assert bob_version in result


# 08. Resolving an Editing Conflict
def test_08_resolving_editing_conflict():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]

    subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, section, ANOTHER_USER], check=True)

    result = subprocess.run(["python", "src/cli.py", "-v", "unlock", TEST_DOC, section, REVIEW_USER], capture_output=True, text=True)
    assert f"{REVIEW_USER} does not have permission" in result.stdout


# 09. Reverting a Section to Its Original State
def test_09_revert_to_original_state():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]

    result = subprocess.run(["python", "src/cli.py", "list-versions", TEST_DOC, section], capture_output=True, text=True)
    first_version = result.stdout.strip().split("\n")[0].split()[0]
    print(first_version)

    rollback_result = subprocess.run(["python", "src/cli.py", "-v", "rollback-section", TEST_DOC, section, first_version, TEST_USER], capture_output=True, text=True)
    assert "Section restored" in rollback_result.stdout


# 10. Bulk Operations Workflow
def test_10_bulk_operations():
    section = scraibe.list_sections(scraibe.load_document(TEST_DOC))[-1]

    subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, section, TEST_USER], check=True)
    subprocess.run(["python", "src/cli.py", "-v", "lock", TEST_DOC, ANOTHER_SECTION, TEST_USER], check=True)

    subprocess.run(["python", "src/cli.py", "-v", "save-section", TEST_DOC, section, TEST_USER, "Updated Section 1"], check=True)
    subprocess.run(["python", "src/cli.py", "-v", "save-section", TEST_DOC, ANOTHER_SECTION, TEST_USER, "Updated Section 2"], check=True)

    subprocess.run(["python", "src/cli.py", "-v", "unlock", TEST_DOC, section, TEST_USER], check=True)
    subprocess.run(["python", "src/cli.py", "-v", "unlock", TEST_DOC, ANOTHER_SECTION, TEST_USER], check=True)

    result = subprocess.run(["python", "src/cli.py", "-v", "list-versions", TEST_DOC, section], capture_output=True, text=True)
    assert "Updated Section 1" in result.stdout

    result = subprocess.run(["python", "src/cli.py", "-v", "list-versions", TEST_DOC, ANOTHER_SECTION], capture_output=True, text=True)
    assert "Updated Section 2" in result.stdout
