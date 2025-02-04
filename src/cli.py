
import argparse
from src.core.locks import lock_section, is_section_locked, unlock_section
from src.core.versioning import save_section_version, get_version_history, rollback_section

def main():
    parser = argparse.ArgumentParser(description='the scrAIbe - AI-assisted document writing')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Lock Section
    parser_lock = subparsers.add_parser('lock', help='Lock a section for editing')
    parser_lock.add_argument('filename', type=str, help='Document name')
    parser_lock.add_argument('section', type=str, help='Section ID')
    parser_lock.add_argument('user', type=str, help='User who locks the section')

    # Check Lock Status
    parser_check = subparsers.add_parser('check-lock', help='Check if a section is locked')
    parser_check.add_argument('filename', type=str, help='Document name')
    parser_check.add_argument('section', type=str, help='Section ID')

    # Unlock Section
    parser_unlock = subparsers.add_parser('unlock', help='Unlock a section after editing')
    parser_unlock.add_argument('filename', type=str, help='Document name')
    parser_unlock.add_argument('section', type=str, help='Section ID')
    parser_unlock.add_argument('user', type=str, help='User unlocking the section')

    # Save Section Version
    parser_save = subparsers.add_parser('save-section', help='Save a version of a section')
    parser_save.add_argument('filename', type=str, help='Document name')
    parser_save.add_argument('section', type=str, help='Section ID')
    parser_save.add_argument('user', type=str, help='User saving the section')
    parser_save.add_argument('content', type=str, help='New content of the section')

    # List Section Versions
    parser_list_versions = subparsers.add_parser('list-versions', help='List previous versions of a section')
    parser_list_versions.add_argument('filename', type=str, help='Document name')
    parser_list_versions.add_argument('section', type=str, help='Section ID')

    # Rollback Section
    parser_rollback = subparsers.add_parser('rollback-section', help='Rollback to a previous version of a section')
    parser_rollback.add_argument('filename', type=str, help='Document name')
    parser_rollback.add_argument('section', type=str, help='Section ID')
    parser_rollback.add_argument('timestamp', type=str, help='Timestamp of the version to rollback')
    parser_rollback.add_argument('user', type=str, help='User requesting rollback')

    args = parser.parse_args()

    if args.command == 'lock':
        success = lock_section(args.filename, args.section, args.user)
        if success:
            print(f'Section {args.section} locked by {args.user}.')
        else:
            print(f'Error: Section {args.section} is already locked by another user.')

    elif args.command == 'check-lock':
        locking_user = is_section_locked(args.filename, args.section)
        if locking_user:
            print(f'Section {args.section} is locked by {locking_user}.')
        else:
            print(f'Section {args.section} is available.')

    elif args.command == 'unlock':
        success = unlock_section(args.filename, args.section, args.user)
        if success:
            print(f'Section {args.section} unlocked by {args.user}.')
        else:
            print(f'Error: {args.user} does not have permission to unlock section {args.section}.')

    elif args.command == 'save-section':
        version_file = save_section_version(args.filename, args.section, args.user, args.content)
        print(f'Section {args.section} saved as new version: {version_file}')

    elif args.command == 'list-versions':
        history = get_version_history(args.filename, args.section)
        if history:
            print(f'Previous versions of section {args.section}:')
            for version in history:
                print(version)
        else:
            print(f'No previous versions found for section {args.section}.')

    elif args.command == 'rollback-section':
        try:
            content = rollback_section(args.filename, args.section, args.timestamp, args.user)
            print(f'Section {args.section} rolled back to version {args.timestamp}.')
            print('Content:')
            print(content)
        except FileNotFoundError:
            print(f'Error: No version found for section {args.section} at {args.timestamp}.')

if __name__ == '__main__':
    main()

