import pytest
from src.core.markdown_handler import validate_markdown_syntax

@pytest.mark.parametrize("markdown_content, expected_valid, expected_message", [
    # ✅ Valid Markdown
    ("""
>>>>>ID#20250203153000_1
# Introducción
Texto en la sección.
<<<<<ID#20250203153000_1
>>>>>ID#20250203153000_2
## Segunda Sección
Más texto aquí.
<<<<<ID#20250203153000_2
""", True, "Markdown syntax is valid."),

    # ❌ Unclosed section
    ("""
>>>>>ID#20250203153000_1
# Sección sin cierre
Texto sin cierre de sección.
""", False, "Error: Unclosed section(s) found: {'20250203153000_1'}"),

    # ❌ Nested section markers
    ("""
>>>>>ID#20250203153000_1
# Sección principal
>>>>>ID#20250203153000_2
## Sección anidada
Texto en una sección anidada.
<<<<<ID#20250203153000_2
<<<<<ID#20250203153000_1
""", False, "Error: Nested section detected (ID 20250203153000_2 inside 20250203153000_1)."),

    # ❌ Heading outside of a section
    ("""
# Título fuera de sección
Texto fuera de una sección.
""", False, "Error: Heading found outside of a section (# Título fuera de sección)."),

    # ❌ Mismatched section IDs
    ("""
>>>>>ID#20250203153000_1
# Sección con ID incorrecto
Texto con error de cierre de sección.
<<<<<ID#20250203153000_2
""", False, "Error: Closing tag found for unknown section (ID 20250203153000_2)."),

    # ✅ Edge case: Empty document (should be valid)
    ("", True, "Markdown syntax is valid."),
])
def test_validate_markdown_syntax(markdown_content, expected_valid, expected_message):
    """Test various cases of Markdown syntax validation."""
    is_valid, message = validate_markdown_syntax(markdown_content)
    assert is_valid == expected_valid
    assert message == expected_message
