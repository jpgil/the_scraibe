import pytest
from src.core.markdown_handler import repair_markdown_syntax, validate_markdown_syntax

@pytest.mark.parametrize("broken_markdown, expected_fixed, should_repair, should_fail", [
    # Valid document should remain unchanged
    ("""
>>>>>ID#20250205013016_1
# Introduction
Text in the section.
<<<<<ID#20250205013016_1
>>>>>ID#20250205013016_2
## Second Section
More text here.
<<<<<ID#20250205013016_2
""", """
>>>>>ID#20250205013016_1
# Introduction
Text in the section.
<<<<<ID#20250205013016_1
>>>>>ID#20250205013016_2
## Second Section
More text here.
<<<<<ID#20250205013016_2
""", False, False),  # No repair needed, no failure expected

    # Unclosed section → Should be auto-closed
    ("""
>>>>>ID#20250205013016_1
# Unclosed section
Text without section closure.
""", """
>>>>>ID#20250205013016_1
# Unclosed section
Text without section closure.


<<<<<ID#20250205013016_1
""", True, False),  # Repair needed, no failure

    # Nested section markers → Should be split into separate sections
    ("""
>>>>>ID#20250205013016_1
# Main section
>>>>>ID#20250205013016_2
## Nested section
Text in a nested section.
<<<<<ID#20250205013016_2
<<<<<ID#20250205013016_1
""", """
>>>>>ID#20250205013016_1
# Main section
<<<<<ID#20250205013016_1
>>>>>ID#20250205013016_2
## Nested section
Text in a nested section.
<<<<<ID#20250205013016_2
""", True, True),  # Repair needed, fails!

    # Heading outside of a section → Should be wrapped in a new section
    ("""
# Heading outside of section
Text outside of a section.
""", """
>>>>>ID#20250205013016_1
# Heading outside of section
Text outside of a section.


<<<<<ID#20250205013016_1
""", True, False),  # Repair needed, no failure

    # Mismatched section IDs → Should correct IDs
    ("""
>>>>>ID#20250205013016_1
# Section with incorrect ID
Text with section closure error.
<<<<<ID#20250205013016_2
""", """
>>>>>ID#20250205013016_1
# Section with incorrect ID
Text with section closure error.
<<<<<ID#20250205013016_1
""", True, True)  # Repair needed, fails!
])


def test_repair_markdown_syntax(broken_markdown, expected_fixed, should_repair, should_fail):
    """Test repairing various broken Markdown structures."""
    is_valid_before, _ = validate_markdown_syntax(broken_markdown)

    if should_fail:
        # If repair is impossible, expect an exception
        with pytest.raises(ValueError) as excinfo:
            repair_markdown_syntax(broken_markdown)
        assert "Repair failed" in str(excinfo.value)
    else:
        # Otherwise, attempt repair
        repaired_content = f"{repair_markdown_syntax(broken_markdown, force_timestamp='20250205013016')}"
        is_valid_after, _ = validate_markdown_syntax(repaired_content)
        
        if should_repair:
            print()
            print(f"Repaired:\n'{repaired_content.strip()}'\nexpected_fixed:\n'{expected_fixed.strip()}'")
            assert repaired_content.strip() == expected_fixed.strip()
            assert is_valid_after
        else:
            # If no repair was needed, output should be unchanged
            assert repaired_content.strip() == broken_markdown.strip()
            assert is_valid_before
