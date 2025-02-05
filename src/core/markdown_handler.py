import time
import os
import re
import datetime
from src.core.locks import is_section_locked
from src.core.versioning import save_section_version



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
    lines = content.splitlines()
    for line in lines:
        if line.startswith('>>>>>ID#'):
            section_id = line.strip().replace('>>>>>ID#', '')
            sections.append(section_id)
    return sections

def load_section(filename: str, section_id: str) -> str:
    if not os.path.exists(filename):
        raise FileNotFoundError(f'El archivo {filename} no existe.')
    else:
        content = load_document(filename)
        return extract_section(content, section_id)
    
def extract_section(content: str, section_id: str) -> str:
    """Extrae y devuelve el contenido de una sección específica."""
    lines = content.splitlines()
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

    return "\n".join(section_content)

# def save_section(filename: str, section_id: str, user: str, content: str):
#     """Guarda una versión editada de una sección específica."""
#     filename = os.path.basename(filename)
#     version_filename = f'versions/{filename}.section_{section_id}.{user}.md'
#     with open(version_filename, 'w', encoding='utf-8') as f:
#         f.write(content)


def save_section(filename: str, section_id: str, user: str, new_content: str):
    """Saves a new version of a section but prevents modification if it's locked by another user."""

    # Check if section is locked and by whom
    # Wait at most 1s to unlock
    locking_user = is_section_locked(filename, section_id)
    TRIES = 10
    while TRIES>0 and locking_user and locking_user != user:
        TRIES -= 1
        time.sleep(0.1)
        print(f"Waiting for {locking_user} unlocking {filename} ... {TRIES}")
        locking_user = is_section_locked(filename, section_id)
    
    locking_user = is_section_locked(filename, section_id)
    if locking_user and locking_user != user:
        raise PermissionError(f"Error: Section {section_id} is locked by {locking_user}. Cannot save changes.")

    # Check section exists
    existing_sections = list_sections(load_document(filename))
    if section_id not in existing_sections:
        raise ValueError(f"Error: Section {section_id} does not exist in the document.")

    # Read the document
    doc_original = load_document(filename)
    lines = doc_original.splitlines()

    # with open(filename, "r", encoding="utf-8") as f:
    #     lines = f.readlines()
        
    # Validate the new content syntax
    is_valid, message = validate_markdown_syntax("\n".join(lines))
    if not is_valid:
        raise ValueError(f"Error: Invalid Markdown syntax in new content. {message}")

    # Process lines and update section content
    in_target_section = False
    in_previous = True
    # updated_lines = []
    previous_lines = []
    next_lines = []
    for line in lines:
        if line.strip() == f">>>>>ID#{section_id}":
            in_target_section = True
            previous_lines.append(line)
            
        elif in_target_section and line.startswith("<<<<<ID#"):
            in_target_section = False  # End of section
            in_previous = False
            next_lines.append(line)

        elif not in_target_section:
            if in_previous:
                previous_lines.append(line)
            else:
                next_lines.append(line)
    
    updated_lines = previous_lines + new_content.strip().splitlines() + next_lines

    # Save the version
    version_filename = save_section_version(filename, section_id, user, new_content)

    # Save the modified document
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines) + "\n")
        
    # Reload to see if it wrote ok
    reloaded_content = load_document(filename)
    if "\n".join(updated_lines) not in reloaded_content:
        # Restore the original
        with open(filename, "w", encoding="utf-8") as f:
            f.write(doc_original)
        raise IOError(f"Error: Failed to write new content to section {section_id}.")

    return version_filename

        
        
def generate_section_id(index: int) -> str:
    """Generates a unique section ID based on timestamp and index."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return f'{timestamp}_{index}'

def add_section_markers(content: str) -> str:
    """Adds section markers to a Markdown document if they don't exist."""
    lines = content.split("\n")
    new_content = []
    section_index = 1
    inside_existing_section = False
    current_section_id = None

    for i, line in enumerate(lines):
        # Detect existing section markers
        if re.match(r"^>>>>>ID#\d+_\d+$", line):
            inside_existing_section = True
            new_content.append(line)
            continue
        elif re.match(r"^<<<<<ID#\d+_\d+$", line):
            inside_existing_section = False
            new_content.append(line)
            continue

        # Detect headings (`#`, `##`, `###`, etc.)
        if re.match(r"^\s*#+\s", line) and not inside_existing_section:
            # If there's an open section, close it before starting a new one
            if current_section_id:
                new_content.append(f"<<<<<ID#{current_section_id}")

            # Generate new section ID
            current_section_id = generate_section_id(section_index)
            new_content.append(f">>>>>ID#{current_section_id}")
            section_index += 1

        new_content.append(line)

    # Ensure the last section is closed
    if current_section_id:
        new_content.append(f"<<<<<ID#{current_section_id}")

    return "\n".join(new_content)


def load_and_label_document(filename: str) -> str:
    """Loads a Markdown document and ensures it has section markers."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f'Error: File {filename} not found.')

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add section markers if they are missing
    labeled_content = add_section_markers(content)

    # Save the document with labeled sections
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(labeled_content)

    return labeled_content

# def load(filename: str) -> str:
#     return load_and_label_document(str)



def validate_markdown_syntax(content: str) -> bool:
    """Checks if the Markdown file follows the correct section structure."""
    lines = content.split("\n")
    open_sections = set()
    section_active = False
    last_section_id = None

    for line in lines:
        # Detect section opening
        match_open = re.match(r"^>>>>>ID#(\d+_\d+)$", line.strip())
        if match_open:
            section_id = match_open.group(1)
            if section_active:
                return False, f"Error: Nested section detected (ID {section_id} inside {last_section_id})."
            open_sections.add(section_id)
            section_active = True
            last_section_id = section_id
            continue

        # Detect section closing
        match_close = re.match(r"^<<<<<ID#(\d+_\d+)$", line.strip())
        if match_close:
            section_id = match_close.group(1)
            if section_id not in open_sections:
                return False, f"Error: Closing tag found for unknown section (ID {section_id})."
            open_sections.remove(section_id)
            section_active = False
            last_section_id = None
            continue

        # Detect a heading outside of a section
        if re.match(r"^\s*#+\s", line) and not section_active:
            return False, f"Error: Heading found outside of a section ({line.strip()})."

    if open_sections:
        return False, f"Error: Unclosed section(s) found: {open_sections}"

    return True, "Markdown syntax is valid."



def repair_markdown_syntax(content: str) -> str:
    """Attempts to fix incorrect Markdown section syntax."""
    # Pre-check: Validate before repairing
    is_valid, message = validate_markdown_syntax(content)
    if is_valid:
        return content  # No repair needed

    # print(f"Repairing document due to: {message}")

    lines = content.split("\n")
    new_content = []
    open_sections = set()
    section_id_counter = 1
    last_section_id = None
    inside_section = False

    for line in lines:
        # Detect section opening
        match_open = re.match(r"^>>>>>ID#(\d+_\d+)$", line.strip())
        if match_open:
            section_id = match_open.group(1)
            if inside_section:
                new_content.append(f"<<<<<ID#{last_section_id}")  # Close previous section
            open_sections.add(section_id)
            last_section_id = section_id
            inside_section = True
            new_content.append(line)
            continue

        # Detect section closing
        match_close = re.match(r"^<<<<<ID#(\d+_\d+)$", line.strip())
        if match_close:
            section_id = match_close.group(1)
            if section_id in open_sections:
                open_sections.remove(section_id)
            inside_section = False
            last_section_id = None
            new_content.append(line)
            continue

        # Detect heading outside of a section
        if re.match(r"^\s*#+\s", line) and not inside_section:
            if last_section_id:
                new_content.append(f"<<<<<ID#{last_section_id}")  # Close previous section
            
            # Create a new section ID
            new_section_id = f"20250203153000_{section_id_counter}"
            section_id_counter += 1
            open_sections.add(new_section_id)
            last_section_id = new_section_id
            inside_section = True
            
            new_content.append(f">>>>>ID#{new_section_id}")
            new_content.append(line)
            continue

        new_content.append(line)

    # Ensure all open sections are closed
    if inside_section and last_section_id:
        new_content.append(f"<<<<<ID#{last_section_id}")

    repaired_content = "\n".join(new_content)
    repaired_content = repaired_content.replace("\n<<<<<ID#", "<<<<<ID#").strip()
    repaired_content += "\n"

    # Post-check: Validate after repairing
    is_valid, message = validate_markdown_syntax(repaired_content)
    if not is_valid:
        raise ValueError(f"Repair failed: {message}")

    return repaired_content
