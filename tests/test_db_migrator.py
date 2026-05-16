import sqlite3
import os
from db_migrator import create_schema

def test_create_schema():
    db_path = "test_audit.db"
    if os.path.exists(db_path): os.remove(db_path)
    create_schema(db_path)
    with sqlite3.connect(db_path) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t[0] for t in tables]
        assert "Vendors" in table_names
        assert "Invoices" in table_names
        assert "Payments" in table_names
        assert "Receipts" in table_names
        assert "Contracts" in table_names
    os.remove(db_path)
