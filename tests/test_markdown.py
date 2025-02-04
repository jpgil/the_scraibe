
import os
import pytest
from src.core.markdown_handler import load_document, save_document, list_sections, load_section, save_section

TEST_DOC_PATH = 'documents/test_document.md'

@pytest.fixture
def sample_markdown():
    return """
>>>>>ID#20250203153000_1
# Introducción
Este es el contenido de la introducción.
<<<<<ID#20250203153000_1

>>>>>ID#20250203153000_2
## Segunda Sección
Texto de prueba aquí.
<<<<<ID#20250203153000_2
"""

# Test 1: Cargar un documento existente
def test_load_document_exists():
    content = '# Test Document\nEste es un test.'
    with open(TEST_DOC_PATH, 'w') as f:
        f.write(content)

    loaded_content = load_document(TEST_DOC_PATH)
    assert loaded_content == content

    os.remove(TEST_DOC_PATH)

# Test 2: Intentar cargar un documento que no existe
def test_load_document_not_found():
    with pytest.raises(FileNotFoundError):
        load_document('documents/_______nonexistent.md')

# Test 3: Guardar un documento y verificar su contenido
def test_save_document():
    content = 'Nuevo contenido del documento.'
    save_document(TEST_DOC_PATH, content)

    with open(TEST_DOC_PATH, 'r') as f:
        assert f.read() == content

    os.remove(TEST_DOC_PATH)

# Test 4: Listar secciones correctamente
def test_list_sections(sample_markdown):
    sections = list_sections(sample_markdown)
    assert sections == ['20250203153000_1', '20250203153000_2']

# Test 5: Cargar una sección específica
def test_load_section(sample_markdown):
    section_content = load_section(sample_markdown, '20250203153000_1')
    assert section_content.strip() == '# Introducción\nEste es el contenido de la introducción.'

# Test 6: Error al cargar una sección inexistente
def test_load_section_not_found(sample_markdown):
    with pytest.raises(ValueError):
        load_section(sample_markdown, '99999999999999')

# Test 7: Guardar una sección editada
def test_save_section():
    section_id = '20250203153000_1'
    user = 'jgil'
    content = 'Contenido modificado de la sección.'

    save_section('test_document.md', section_id, user, content)

    saved_file = f'versions/test_document.md.section_{section_id}.{user}.md'
    with open(saved_file, 'r') as f:
        assert f.read() == content

    os.remove(saved_file)

