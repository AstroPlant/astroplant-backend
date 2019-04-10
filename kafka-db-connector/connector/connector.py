import argparse
from database import DatabaseManager

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        choices=[
            'setup-schema',
            'insert-develop-data',
            'run',
        ],
    )
    parser.parse_args()
    args = parser.parse_args()

    db = DatabaseManager()
    if args.command == 'setup-schema':
        db.setup_schema()
    elif args.command == 'insert-develop-data':
        db.insert_develop_data()
    elif args.command == 'run':
        raise NotImplementedError()

