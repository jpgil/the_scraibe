
import os
import glob
import datetime
import re


def save_section_version(filename: str, section_id: str, user: str, content: str):
    """Saves a version of an edited section."""
    filename = os.path.basename(filename)
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    version_filename = f'versions/{filename}.section_{section_id}.{timestamp}.{user}.md'
    
    os.makedirs('versions', exist_ok=True)

    with open(version_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return version_filename

def get_all_versions(filename: str):
    """Returns a list of all versions of a file."""
    filename = os.path.basename(filename)
    pattern = f'versions/{filename}.section_*.*.md'
    version_files = sorted(glob.glob(pattern), reverse=True)

    matches = []

    for filename in version_files:
        match = re.search(r"versions/(?P<filename>[^/]+)\.section_(?P<section_id>\d+_\d+)\.(?P<timestamp>\d+)\.(?P<user>[^/]+)\.md", filename)
        if match:
            matches.append({
                "filename": match.group("filename"),
                "section_id": match.group("section_id"),
                "timestamp": match.group("timestamp"),
                "user": match.group("user"),
            })
    matches.sort(key=lambda x: x['timestamp'], reverse=True)
    return matches
    
def get_version_history(filename: str, section_id: str):
    all_versions = get_all_versions(filename)
    return [ v for v in all_versions if v['section_id']==section_id ]



def rollback_section(filename: str, section_id: str, timestamp: str, user: str):
    """Restores a previous version of a section."""
    filename = os.path.basename(filename)
    version_filename = f'versions/{filename}.section_{section_id}.{timestamp}.{user}.md'

    if not os.path.exists(version_filename):
        raise FileNotFoundError(f'No version found for section {section_id} at {timestamp}')
    
    with open(version_filename, 'r', encoding='utf-8') as f:
        return f.read()

