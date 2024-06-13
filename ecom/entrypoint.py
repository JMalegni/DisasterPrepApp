import os
import sys
import sqlite3
from datetime import datetime

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Connect to the SQLite database
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'db.sqlite3'))
    cursor = conn.cursor()

    # Check if the migrations table exists
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name='django_migrations';
    """)
    table_exists = cursor.fetchone()

    # Run migrations only if the migrations table does not exist
    if not table_exists:
        execute_from_command_line(['manage.py', 'migrate'])

    # Close the connection
    cursor.close()
    conn.close()

    # Run the server
    execute_from_command_line(sys.argv + ['runserver'])

if __name__ == '__main__':
    main()
