import os
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

    db = DatabaseManager(
        host=os.environ.get('DATABASE_HOST', 'database.ops'),
        port=int(os.environ.get('DATABASE_PORT', '5432')),
        user=os.environ.get('DATABASE_USER', 'astroplant'),
        password=os.environ.get('DATABASE_PASSWORD', 'astroplant'),
        database=os.environ.get('DATABASE_DATABASE', 'astroplant'),
    )
    if args.command == 'setup-schema':
        db.setup_schema()
    elif args.command == 'insert-develop-data':
        db.insert_develop_data()
    elif args.command == 'run':
        raise NotImplementedError()

