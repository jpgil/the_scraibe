
import os
import glob
import datetime


def save_section_version(filename: str, section_id: str, user: str, content: str):
    """Saves a version of an edited section."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    version_filename = f'versions/{filename}.section_{section_id}.{timestamp}.{user}.md'
    
    os.makedirs('versions', exist_ok=True)

    with open(version_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return version_filename

def get_version_history(filename: str, section_id: str):
    """Returns a list of previous versions of a section."""
    pattern = f'versions/{filename}.section_{section_id}.*.md'
    version_files = sorted(glob.glob(pattern), reverse=True)
    
    return version_files

def rollback_section(filename: str, section_id: str, timestamp: str, user: str):
    """Restores a previous version of a section."""
    version_filename = f'versions/{filename}.section_{section_id}.{timestamp}.{user}.md'

    if not os.path.exists(version_filename):
        raise FileNotFoundError(f'No version found for section {section_id} at {timestamp}')
    
    with open(version_filename, 'r', encoding='utf-8') as f:
        return f.read()

