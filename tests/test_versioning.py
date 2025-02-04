
import os
import pytest
import datetime
from src.core.versioning import save_section_version, get_version_history, rollback_section

TEST_DOC = 'test_document.md'
TEST_SECTION = '20250203153000_1'
TEST_USER = 'jgil'

@pytest.fixture
def sample_version():
    """Creates a sample section version for testing."""
    content = 'This is a test version.'
    return save_section_version(TEST_DOC, TEST_SECTION, TEST_USER, content)

def test_save_section_version():
    content = 'New version of the section.'
    version_file = save_section_version(TEST_DOC, TEST_SECTION, TEST_USER, content)

    assert os.path.exists(version_file)

    with open(version_file, 'r') as f:
        assert f.read() == content

    os.remove(version_file)

def test_get_version_history(sample_version):
    history = get_version_history(TEST_DOC, TEST_SECTION)
    assert len(history) > 0
    assert sample_version in [ f"versions/{h['filename']}.section_{TEST_SECTION}.{h['timestamp']}.{h['user']}.md" for h in history ]
    # assert any([ os.path.basename(sample_version) == h['filename'] for h in history ])

def test_rollback_section(sample_version):
    restored_content = rollback_section(TEST_DOC, TEST_SECTION, sample_version.split('.')[-3], TEST_USER)
    assert restored_content == 'This is a test version.'

@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    if os.path.exists(TEST_DOC):
        os.remove(TEST_DOC)