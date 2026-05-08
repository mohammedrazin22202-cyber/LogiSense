"""
Fleet Command - MySQL Configuration
Edit the values below to match your MySQL server setup.
"""

DB_CONFIG = {
    'host':     'localhost',
    'port':     3306,
    'user':     'root',       # ← change to your MySQL username
    'password': '',           # ← change to your MySQL password
    'database': 'fleet_command',
    'charset':  'utf8mb4',
    'autocommit': False,
    'connection_timeout': 10,
}

# Database name (used by seed.py to CREATE DATABASE if not exists)
DB_NAME = DB_CONFIG['database']
