import os
import pytest
import tempfile
import shutil
from src.core import load_document, save_document, list_sections, load_section, save_section
from src.core import delete_document, get_filename_path, VERSION_DIR, LOCKS_DIR

TEST_DOC_PATH = 'documents/test_document.md'

@pytest.fixture
def sample_markdown():
    """Provides sample Markdown content with sections."""
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

@pytest.fixture(autouse=True)
def setup_and_cleanup(sample_markdown):
    """Writes sample Markdown content before each test and ensures cleanup after."""
    os.makedirs(os.path.dirname(TEST_DOC_PATH), exist_ok=True)

    # Before test: Write test document
    with open(TEST_DOC_PATH, 'w', encoding='utf-8') as f:
        f.write(sample_markdown)

    yield  # Run the test

    # After test: Clean up the file
    if os.path.exists(TEST_DOC_PATH):
        os.remove(TEST_DOC_PATH)

# Test 1: Cargar un documento existente
def test_01_load_document_exists():
    loaded_content = load_document(TEST_DOC_PATH)
    with open(TEST_DOC_PATH, 'r', encoding='utf-8') as f:
        expected_content = f.read()

    assert loaded_content == expected_content

# Test 2: Intentar cargar un documento que no existe
def test_02_load_document_not_found():
    with pytest.raises(FileNotFoundError):
        load_document('documents/_______nonexistent.md')

# Test 3: Guardar un documento y verificar su contenido
def test_03_save_document():
    content = 'Nuevo contenido del documento.'
    save_document(TEST_DOC_PATH, content)

    with open(TEST_DOC_PATH, 'r', encoding='utf-8') as f:
        assert f.read() == content

# Test 4: Listar secciones correctamente
def test_04_list_sections():
    loaded_content = load_document(TEST_DOC_PATH)    
    sections = list_sections(loaded_content)
    assert sections == ['20250203153000_1', '20250203153000_2']

# Test 5: Cargar una sección específica
def test_05_load_section():
    section_content = load_section(TEST_DOC_PATH, '20250203153000_1')
    assert section_content.strip() == '# Introducción\nEste es el contenido de la introducción.'

# Test 6: Error al cargar una sección inexistente
def test_06_load_section_not_found():
    with pytest.raises(ValueError):
        load_section(TEST_DOC_PATH, '99999999999999')

# Test 7: Guardar una sección editada
def test_07_save_section():
    section_id = '20250203153000_1'
    user = 'jgil'
    content = 'Contenido modificado de la sección.'
    save_section(TEST_DOC_PATH, section_id, user, content)

    # saved_file = f'versions/test_document.md.section_{section_id}.{user}.md'
    
    # with open(saved_file, 'r', encoding='utf-8') as f:
    #     assert f.read() == content

    # os.remove(saved_file)  # Cleanup versioned file after test




def test_08_delete_document_success(tmp_path):
    # Setup temporary directories for documents, versions, and locks
    doc_name = "temp_test_doc.md"
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir(exist_ok=True)
    doc_path = documents_dir / doc_name
    doc_path.write_text("# Temporary Document\nContent")

    # Create dummy versions directory for this document
    versions_doc_dir = tmp_path / "versions" / doc_name
    versions_doc_dir.mkdir(parents=True, exist_ok=True)
    version_file = versions_doc_dir / f"{doc_name}.section_12345.user.md"
    version_file.write_text("Version content")

    # Create dummy locks directory for this document
    locks_doc_dir = tmp_path / "locks" / doc_name
    locks_doc_dir.mkdir(parents=True, exist_ok=True)
    lock_file = locks_doc_dir / f"{doc_name}.section_12345.lock"
    lock_file.write_text("Lock content")

    # Monkey-patch the globals in scraibe so that delete_document uses the tmp_path directories.
    # (Adjust these if your module names differ.)
    import src.core.markdown_handler as scraibe_module
    original_version_dir = scraibe_module.VERSION_DIR
    original_locks_dir = scraibe_module.LOCKS_DIR
    original_get_filename_path = scraibe_module.get_filename_path
    
    scraibe_module.VERSION_DIR = str(tmp_path / "versions")
    scraibe_module.LOCKS_DIR = str(tmp_path / "locks")
    scraibe_module.get_filename_path = lambda filename, check_path=False: str(doc_path)

    try:
        # Call delete_document
        result = delete_document(str(doc_path))
        assert result is True

        # Verify that the document and its related version and lock directories are removed
        assert not doc_path.exists()
        assert not (tmp_path / "versions" / doc_name).exists()
        assert not (tmp_path / "locks" / doc_name).exists()
    finally:
        # Restore the original directories
        scraibe_module.VERSION_DIR = original_version_dir
        scraibe_module.LOCKS_DIR = original_locks_dir
        scraibe_module.get_filename_path = original_get_filename_path
