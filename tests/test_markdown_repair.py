import pytest
from src.core.markdown_handler import repair_markdown_syntax, validate_markdown_syntax

@pytest.mark.parametrize("broken_markdown, expected_fixed, should_repair, should_fail", [
    # ✅ Valid document should remain unchanged
    ("""
>>>>>ID#20250203153000_1
# Introducción
Texto en la sección.
<<<<<ID#20250203153000_1
>>>>>ID#20250203153000_2
## Segunda Sección
Más texto aquí.
<<<<<ID#20250203153000_2
""", """
>>>>>ID#20250203153000_1
# Introducción
Texto en la sección.
<<<<<ID#20250203153000_1
>>>>>ID#20250203153000_2
## Segunda Sección
Más texto aquí.
<<<<<ID#20250203153000_2
""", False, False),  # No repair needed, no failure expected

    # ❌ Unclosed section → Should be auto-closed
    ("""
>>>>>ID#20250203153000_1
# Sección sin cierre
Texto sin cierre de sección.
""", """
>>>>>ID#20250203153000_1
# Sección sin cierre
Texto sin cierre de sección.
<<<<<ID#20250203153000_1
""", True, False),  # Repair needed, no failure

    # ❌ Nested section markers → Should be split into separate sections
    ("""
>>>>>ID#20250203153000_1
# Sección principal
>>>>>ID#20250203153000_2
## Sección anidada
Texto en una sección anidada.
<<<<<ID#20250203153000_2
<<<<<ID#20250203153000_1
""", """
>>>>>ID#20250203153000_1
# Sección principal
<<<<<ID#20250203153000_1
>>>>>ID#20250203153000_2
## Sección anidada
Texto en una sección anidada.
<<<<<ID#20250203153000_2
""", True, True),  # Repair needed, fails!

    # ❌ Heading outside of a section → Should be wrapped in a new section
    ("""
# Título fuera de sección
Texto fuera de una sección.
""", """
>>>>>ID#20250203153000_1
# Título fuera de sección
Texto fuera de una sección.
<<<<<ID#20250203153000_1
""", True, False),  # Repair needed, no failure

    # ❌ Mismatched section IDs → Should correct IDs
    ("""
>>>>>ID#20250203153000_1
# Sección con ID incorrecto
Texto con error de cierre de sección.
<<<<<ID#20250203153000_2
""", """
>>>>>ID#20250203153000_1
# Sección con ID incorrecto
Texto con error de cierre de sección.
<<<<<ID#20250203153000_1
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
        repaired_content = f"\n{repair_markdown_syntax(broken_markdown)}"
        is_valid_after, _ = validate_markdown_syntax(repaired_content)
        
        if should_repair:
            print()
            print(f"Repaired:\n'{repaired_content}'\n\nTo:'{expected_fixed}'")
            assert repaired_content.strip() == expected_fixed.strip()
            assert is_valid_after
        else:
            # If no repair was needed, output should be unchanged
            assert repaired_content.strip() == broken_markdown.strip()
            assert is_valid_before
