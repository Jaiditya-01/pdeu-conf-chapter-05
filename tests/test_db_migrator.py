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

def test_import_receipts():
    db_path = "test_audit.db"
    csv_path = "warehouse_receipts_fy26.csv"
    if os.path.exists(db_path): os.remove(db_path)
    from db_migrator import create_schema, import_receipts
    create_schema(db_path)
    import_receipts(csv_path, db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT Days_Late FROM Receipts LIMIT 1").fetchone()
        assert row is not None
        # Verify Days_Late is an integer
        assert isinstance(row[0], int)
    os.remove(db_path)

def test_import_contracts():
    db_path = "test_audit.db"
    contracts_dir = "contracts"
    if os.path.exists(db_path): os.remove(db_path)
    from db_migrator import create_schema, import_contracts
    create_schema(db_path)
    # We need some vendors to link contracts to
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO Vendors (Vendor_ID, Vendor_Name) VALUES ('VEN-1000', 'Gujarat Steel Corp')")
    import_contracts(contracts_dir, db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT Penalty_Percentage, Grace_Period_Days FROM Contracts WHERE Vendor_ID='VEN-1000'").fetchone()
        assert row is not None
        assert row[0] == 0.05
        assert row[1] == 7
    os.remove(db_path)
