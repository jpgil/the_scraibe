
import os
import pytest
import datetime
import re
from src.core.versioning import save_section_version, get_version_history, rollback_section
import src.core as scraibe

TEST_DOC = 'documents/test_document.md'
TEST_SECTION = '20250203153000_1'
TEST_USER = 'someuser'

@pytest.fixture(autouse=True)
def setup_and_cleanup(sample_markdown):
    """Writes sample Markdown content before each test and ensures cleanup after."""
    os.makedirs(os.path.dirname(TEST_DOC), exist_ok=True)

    # Before test: Write test document
    with open(TEST_DOC, 'w', encoding='utf-8') as f:
        f.write(sample_markdown)

    yield  # Run the test

    # After test: Clean up the file
    if os.path.exists(TEST_DOC):
        os.remove(TEST_DOC)
    # Remove versions
    version_files = [f for f in os.listdir('versions') if f.startswith(f"{os.path.basename(TEST_DOC)}.section_")]
    for vf in version_files:
        os.remove(os.path.join('versions', vf))
        
@pytest.fixture
def sample_markdown():
    """Provides sample Markdown content with sections."""
    return """
>>>>>ID#20250203153000_1
# Introduction
This is a test version.
<<<<<ID#20250203153000_1
>>>>>ID#20250203153000_2
## Second section
Test content here.
<<<<<ID#20250203153000_2
"""

def test_01_save_section_version():
    content = 'New version of the section.'
    version_file = save_section_version(TEST_DOC, TEST_SECTION, TEST_USER, content)

    assert os.path.exists(version_file)

    with open(version_file, 'r') as f:
        assert f.read() == content

    os.remove(version_file)

def test_02_get_version_history():
    save_section_version(TEST_DOC, TEST_SECTION, "user1", "content1")
    save_section_version(TEST_DOC, TEST_SECTION, "user2", "content2")
    save_section_version(TEST_DOC, TEST_SECTION, "user3", "content3")
    history = get_version_history(TEST_DOC, TEST_SECTION)
    assert len(history) == 3

def test_03_rollback_section():
    version_filename = save_section_version(TEST_DOC, TEST_SECTION, TEST_USER, "content1")
    save_section_version(TEST_DOC, TEST_SECTION, "otheruser", "content2")
    match = re.search(r"versions/(?P<filename>[^/]+)\.section_(?P<section_id>\d+_\d+)\.(?P<timestamp>\d+)\.(?P<user>[^/]+)\.md", version_filename)
    timestamp = match.group("timestamp")

    restored_filename = rollback_section(TEST_DOC, TEST_SECTION, timestamp, TEST_USER)
    assert "section_" in restored_filename
    
    restored_content = scraibe.load_section(TEST_DOC, TEST_SECTION)
    assert restored_content == 'content1'