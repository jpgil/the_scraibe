import argparse
import src.core as scraibe
import sys

def main():
    parser = argparse.ArgumentParser(description='the scrAIbe - AI-assisted document writing')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add labels
    parser_add_labels = subparsers.add_parser('add-labels', help='Add ID labels to a document')
    parser_add_labels.add_argument('filename', type=str, help='Document name')

    # Check Lock Status
    parser_check = subparsers.add_parser('check-lock', help='Check if a section is locked')
    parser_check.add_argument('filename', type=str, help='Document name')
    parser_check.add_argument('section', type=str, help='Section ID')

    # Label Sections
    parser_label = subparsers.add_parser('label-sections', help='Auto-label sections in a Markdown file')
    parser_label.add_argument('filename', type=str, help='Document name')

    # List Sections
    parser_list_sections = subparsers.add_parser('list-sections', help='List all sections in a Markdown file')
    parser_list_sections.add_argument('filename', type=str, help='Document name')

    # List Section Versions
    parser_list_versions = subparsers.add_parser('list-versions', help='List previous versions of a section')
    parser_list_versions.add_argument('filename', type=str, help='Document name')
    parser_list_versions.add_argument('section', type=str, help='Section ID')

    # Lock Section
    parser_lock = subparsers.add_parser('lock', help='Lock a section for editing')
    parser_lock.add_argument('filename', type=str, help='Document name')
    parser_lock.add_argument('section', type=str, help='Section ID')
    parser_lock.add_argument('user', type=str, help='User who locks the section')

    # Rollback Section
    parser_rollback = subparsers.add_parser('rollback-section', help='Rollback to a previous version of a section')
    parser_rollback.add_argument('filename', type=str, help='Document name')
    parser_rollback.add_argument('section', type=str, help='Section ID')
    parser_rollback.add_argument('timestamp', type=str, help='Timestamp of the version to rollback')
    parser_rollback.add_argument('user', type=str, help='User requesting rollback')

    # Save Section Version
    parser_save = subparsers.add_parser('save-section', help='Save a version of a section')
    parser_save.add_argument('filename', type=str, help='Document name')
    parser_save.add_argument('section', type=str, help='Section ID')
    parser_save.add_argument('user', type=str, help='User saving the section')
    parser_save.add_argument('content', type=str, help='New content of the section')

    # Unlock Section
    parser_unlock = subparsers.add_parser('unlock', help='Unlock a section after editing')
    parser_unlock.add_argument('filename', type=str, help='Document name')
    parser_unlock.add_argument('section', type=str, help='Section ID')
    parser_unlock.add_argument('user', type=str, help='User unlocking the section')

    # Validate Markdown Syntax
    parser_validate = subparsers.add_parser('validate-syntax', help='Validate the syntax of a Markdown file')
    parser_validate.add_argument('filename', type=str, help='Document name')

    # Version History
    parser_version_history = subparsers.add_parser('version-history', help='Show version history of a section')
    parser_version_history.add_argument('filename', type=str, help='Document name')
    parser_version_history.add_argument('section', type=str, help='Section ID')

    def verbose_print(verbose, message):
        if verbose:
            print(message)

    args = parser.parse_args()

    if args.command == 'lock':
        success = scraibe.lock_section(args.filename, args.section, args.user)
        if success:
            verbose_print(args.verbose, f'Section {args.section} locked by {args.user}.')
        else:
            print(f'Error: Section {args.section} is already locked by another user.')
            sys.exit(1)

    elif args.command == 'check-lock':
        locking_user = scraibe.is_section_locked(args.filename, args.section)
        if locking_user:
            print(f'Section {args.section} is locked by {locking_user}.')
            sys.exit(1)
        else:
            print(f'Section {args.section} is available.')

    elif args.command == 'unlock':
        success = scraibe.unlock_section(args.filename, args.section, args.user)
        if success:
            verbose_print(args.verbose, f'Section {args.section} unlocked by {args.user}.')
        else:
            print(f'Error: {args.user} does not have permission to unlock section {args.section}.')
            sys.exit(1)

    elif args.command == 'save-section':
        version = scraibe.save_section(args.filename, args.section, args.user, args.content)
        verbose_print(args.verbose, f'Section {args.section} saved as new version:')
        print(version)

    elif args.command == 'list-versions':
        history = scraibe.get_version_history(args.filename, args.section)
        if history:
            verbose_print(args.verbose, f'Previous versions of section {args.section}:')
            for version in history:
                print(f"{version['timestamp']} {version['user']}")
        else:
            verbose_print(args.verbose, f'No previous versions found for section {args.section}.')

    elif args.command == 'rollback-section':
        try:
            content = scraibe.rollback_section(args.filename, args.section, args.timestamp, args.user)
            print(f'Section {args.section} rolled back to version {args.timestamp}.')
            verbose_print(args.verbose, 'Content:')
            verbose_print(args.verbose, content)
        except FileNotFoundError:
            print(f'Error: No version found for section {args.section} at {args.timestamp}.')
            sys.exit(1)

    elif args.command == 'label-sections':
        labeled_content = scraibe.load_and_label_document(args.filename)
        verbose_print(args.verbose, f'Document {args.filename} has been labeled with section markers.')

    elif args.command == 'list-sections':
        try:
            content = scraibe.load_document(args.filename)
            sections = scraibe.list_sections(content)
            verbose_print(args.verbose, f"Sections in {args.filename}:")
            for section_id in sections:
                print(f"{section_id}")
        except FileNotFoundError as e:
            print(str(e))
            sys.exit(1)

    elif args.command == 'validate-syntax':
        try:
            content = scraibe.load_document(args.filename)
            is_valid, message = scraibe.validate_markdown_syntax(content)
            if is_valid:
                print(f'Syntax validation passed: {message}')
            else:
                print(f'Syntax validation failed: {message}')
                sys.exit(1)
        except FileNotFoundError as e:
            print(str(e))
            sys.exit(1)
            
    elif args.command == 'version-history':
        history = scraibe.get_version_history(args.filename, args.section)
        if history:
            verbose_print(args.verbose, f'Previous versions of section {args.section}:')
            for version in history:
                print(f"{version['timestamp']} by {version['user']}")
        else:
            verbose_print(args.verbose, f'No previous versions found for section {args.section}.')

    elif args.command == 'add-labels':
        content = scraibe.load_document(args.filename)
        lbl1 = scraibe.add_section_markers(content)
        lbl1 = scraibe.repair_markdown_syntax(lbl1)
        valid, msg = scraibe.validate_markdown_syntax(lbl1)
        if not valid:
            print(msg)
            raise(f"The document {args.filename} has bad sintaxis, fix it manually")
        result = scraibe.save_document(args.filename, lbl1)
        verbose_print(args.verbose, f"Document {args.filename} labelled.")

if __name__ == '__main__':
    main()


