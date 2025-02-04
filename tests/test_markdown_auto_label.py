
import os
import pytest
from src.core.markdown_handler import add_section_markers

@pytest.fixture
def sample_markdown():
    return """
# Introduction
Some text here.

## Background
More text.

### Details
Even more details.
"""

def test_add_section_markers(sample_markdown):
    """Ensure that section markers are correctly added to a Markdown file."""
    processed = add_section_markers(sample_markdown)
    assert '>>>>>ID#' in processed
    assert '<<<<<ID#' in processed

