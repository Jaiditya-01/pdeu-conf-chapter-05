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

def test_migrate_ledger():
    db_path = "test_audit.db"
    source_db = "ap_ledger.db"
    if os.path.exists(db_path): os.remove(db_path)
    from db_migrator import create_schema, migrate_ledger
    create_schema(db_path)
    migrate_ledger(source_db, db_path)
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM Vendors").fetchone()[0]
        assert count > 0
    os.remove(db_path)
