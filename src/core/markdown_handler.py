
import os
import datetime

def load_document(filename: str) -> str:
    """Carga el contenido de un documento Markdown."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f'El archivo {filename} no existe.')
    
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def save_document(filename: str, content: str):
    """Guarda el contenido de un documento Markdown."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    except PermissionError:
        raise PermissionError(f'No tienes permisos para escribir en {filename}.')

def list_sections(content: str) -> list:
    """Devuelve una lista de secciones con sus IDs."""
    sections = []
    lines = content.split('\n')
    for line in lines:
        if line.startswith('>>>>>ID#'):
            section_id = line.strip().replace('>>>>>ID#', '')
            sections.append(section_id)
    return sections

def load_section(content: str, section_id: str) -> str:
    """Extrae y devuelve el contenido de una sección específica."""
    lines = content.split('\n')
    inside_section = False
    section_content = []
    
    for line in lines:
        if line.strip() == f'>>>>>ID#{section_id}':
            inside_section = True
            continue  # No incluir la línea del marcador de inicio
        
        if line.strip() == f'<<<<<ID#{section_id}':
            inside_section = False
            break
        
        if inside_section:
            section_content.append(line)
    
    if not section_content:
        raise ValueError(f'La sección {section_id} no fue encontrada.')

    return '\n'.join(section_content)

def save_section(filename: str, section_id: str, user: str, content: str):
    """Guarda una versión editada de una sección específica."""
    version_filename = f'versions/{filename}.section_{section_id}.{user}.md'
    with open(version_filename, 'w', encoding='utf-8') as f:
        f.write(content)

