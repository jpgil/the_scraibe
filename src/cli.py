
import argparse
from src.core.locks import lock_section, is_section_locked, unlock_section
from src.core.markdown_handler import load_document, save_section

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

if __name__ == '__main__':
    main()

