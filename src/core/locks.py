
import os
import yaml
import datetime

LOCKS_DIR = 'locks'

def lock_section(filename: str, section_id: str, user: str) -> bool:
    """Locks a section for editing by a user."""
    
    filename = os.path.basename(filename)
    os.makedirs(f"{LOCKS_DIR}/{filename}", exist_ok=True)
    lock_file = f'{LOCKS_DIR}/{filename}/{filename}.section_{section_id}.lock'

    if os.path.exists(lock_file):
        with open(lock_file, 'r', encoding='utf-8') as f:
            lock_data = yaml.safe_load(f)
            if lock_data['user'] != user:
                return False  # Section already locked by another user

    lock_data = {
        'section': section_id,
        'user': user,
        'locked_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(lock_file, 'w', encoding='utf-8') as f:
        yaml.dump(lock_data, f)

    return True

def is_section_locked(filename: str, section_id: str) -> str:
    """Checks if a section is locked and returns the locking user."""
    filename = os.path.basename(filename)
    lock_file = f'{LOCKS_DIR}/{filename}/{filename}.section_{section_id}.lock'

    if os.path.exists(lock_file):
        with open(lock_file, 'r', encoding='utf-8') as f:
            lock_data = yaml.safe_load(f)
            return lock_data['user']

    return None

def unlock_section(filename: str, section_id: str, user: str) -> bool:
    filename = os.path.basename(filename)
    """Unlocks a section if the user owns the lock."""
    lock_file = f'{LOCKS_DIR}/{filename}/{filename}.section_{section_id}.lock'

    if not os.path.exists(lock_file):
        return False  # No lock found

    with open(lock_file, 'r', encoding='utf-8') as f:
        lock_data = yaml.safe_load(f)

    if lock_data['user'] != user:
        return False  # Only the locking user can unlock

    os.remove(lock_file)
    return True

def check_all_locks(filename: str) -> dict:
    """Verify if any user has locked sections of this document."""
    locks = {}

    for lock_file in os.listdir(f"{LOCKS_DIR}/{filename}/"):
        if lock_file.startswith(filename) and lock_file.endswith('.lock'):
            section_id = lock_file.split('.section_')[1].split('.lock')[0]
            with open(f'{LOCKS_DIR}/{filename}/{lock_file}', 'r', encoding='utf-8') as f:
                lock_data = yaml.safe_load(f)
                locks[section_id] = lock_data['user']

    return locks
    