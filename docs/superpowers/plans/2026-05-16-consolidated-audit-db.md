# Consolidated Audit Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate financial, delivery, and legal data into a single SQLite database.

**Architecture:** A Python script `db_migrator.py` will handle the migration. It will use `sqlite3`'s `ATTACH` feature to copy ledger data, `csv` and `datetime` to import and calculate delivery lags, and `re` to parse contract terms.

**Tech Stack:** Python 3.x, `sqlite3`, `csv`, `re`, `pathlib`, `datetime`.

---

### Task 1: Setup and Schema Creation

**Files:**
- Create: `db_migrator.py`
- Test: `tests/test_db_migrator.py`

- [ ] **Step 1: Write failing test for schema creation**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_db_migrator.py::test_create_schema -v`
Expected: FAIL (ImportError or AttributeError)

- [ ] **Step 3: Implement `create_schema`**

```python
import sqlite3

def create_schema(db_path):
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE Vendors (Vendor_ID TEXT PRIMARY KEY, Vendor_Name TEXT, GSTIN TEXT, Address TEXT);
            CREATE TABLE Invoices (Invoice_ID TEXT PRIMARY KEY, Vendor_ID TEXT, Amount REAL, Invoice_Date TEXT, Status TEXT, FOREIGN KEY(Vendor_ID) REFERENCES Vendors(Vendor_ID));
            CREATE TABLE Payments (Payment_ID TEXT PRIMARY KEY, Invoice_ID TEXT, Amount REAL, Payment_Date TEXT, FOREIGN KEY(Invoice_ID) REFERENCES Invoices(Invoice_ID));
            CREATE TABLE Receipts (Receipt_ID TEXT PRIMARY KEY, Vendor_ID TEXT, Expected_Delivery TEXT, Actual_Delivery TEXT, Quality_Status TEXT, Days_Late INTEGER, FOREIGN KEY(Vendor_ID) REFERENCES Vendors(Vendor_ID));
            CREATE TABLE Contracts (Vendor_ID TEXT PRIMARY KEY, Contract_Text TEXT, Penalty_Percentage REAL, Grace_Period_Days INTEGER, FOREIGN KEY(Vendor_ID) REFERENCES Vendors(Vendor_ID));
        """)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_db_migrator.py::test_create_schema -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add db_migrator.py tests/test_db_migrator.py
git commit -m "chore: setup migrator and schema creation"
```

---

### Task 2: Migrate Ledger Data

**Files:**
- Modify: `db_migrator.py`
- Test: `tests/test_db_migrator.py`

- [ ] **Step 1: Write test for ledger migration**

```python
def test_migrate_ledger():
    db_path = "test_audit.db"
    source_db = "ap_ledger.db"
    if os.path.exists(db_path): os.remove(db_path)
    create_schema(db_path)
    from db_migrator import migrate_ledger
    migrate_ledger(source_db, db_path)
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM Vendors").fetchone()[0]
        assert count > 0
    os.remove(db_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_db_migrator.py::test_migrate_ledger -v`
Expected: FAIL (AttributeError)

- [ ] **Step 3: Implement `migrate_ledger`**

```python
def migrate_ledger(source_path, target_path):
    with sqlite3.connect(target_path) as conn:
        conn.execute(f"ATTACH DATABASE '{source_path}' AS source")
        conn.execute("INSERT INTO Vendors SELECT * FROM source.Vendors")
        conn.execute("INSERT INTO Invoices SELECT * FROM source.Invoices")
        conn.execute("INSERT INTO Payments SELECT * FROM source.Payments")
        conn.commit()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_db_migrator.py::test_migrate_ledger -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add db_migrator.py
git commit -m "feat: implement ledger migration"
```

---

### Task 3: Import CSV Receipts

**Files:**
- Modify: `db_migrator.py`
- Test: `tests/test_db_migrator.py`

- [ ] **Step 1: Write test for CSV import**

```python
def test_import_receipts():
    db_path = "test_audit.db"
    csv_path = "warehouse_receipts_fy26.csv"
    if os.path.exists(db_path): os.remove(db_path)
    create_schema(db_path)
    from db_migrator import import_receipts
    import_receipts(csv_path, db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT Days_Late FROM Receipts LIMIT 1").fetchone()
        assert row is not None
    os.remove(db_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_db_migrator.py::test_import_receipts -v`
Expected: FAIL

- [ ] **Step 3: Implement `import_receipts`**

```python
import csv
from datetime import datetime

def import_receipts(csv_path, db_path):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            expected = datetime.strptime(row['Expected_Delivery'], '%Y-%m-%d')
            actual = datetime.strptime(row['Actual_Delivery'], '%Y-%m-%d')
            days_late = (actual - expected).days
            data.append((
                row['Receipt_ID'], row['Vendor_ID'], 
                row['Expected_Delivery'], row['Actual_Delivery'], 
                row['Quality_Status'], days_late
            ))
    
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO Receipts VALUES (?, ?, ?, ?, ?, ?)", data
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_db_migrator.py::test_import_receipts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add db_migrator.py
git commit -m "feat: implement CSV receipt import with delay calculation"
```

---

### Task 4: Extract and Import Contracts

**Files:**
- Modify: `db_migrator.py`
- Test: `tests/test_db_migrator.py`

- [ ] **Step 1: Write test for contract extraction**

```python
def test_import_contracts():
    db_path = "test_audit.db"
    contracts_dir = "contracts"
    if os.path.exists(db_path): os.remove(db_path)
    create_schema(db_path)
    # We need some vendors to link contracts to
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO Vendors (Vendor_ID, Vendor_Name) VALUES ('VEN-1000', 'Aurora LLC')")
    from db_migrator import import_contracts
    import_contracts(contracts_dir, db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT Penalty_Percentage, Grace_Period_Days FROM Contracts WHERE Vendor_ID='VEN-1000'").fetchone()
        assert row == (0.05, 7)
    os.remove(db_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_db_migrator.py::test_import_contracts -v`
Expected: FAIL

- [ ] **Step 3: Implement `import_contracts`**

```python
import re
import os
from pathlib import Path

def import_contracts(contracts_dir, db_path):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        vendors = {row['Vendor_Name']: row['Vendor_ID'] for row in conn.execute("SELECT Vendor_Name, Vendor_ID FROM Vendors").fetchall()}
        
        contract_data = []
        for file_path in Path(contracts_dir).glob("*.txt"):
            vendor_name = file_path.stem.replace("_Contract", "").replace("_", " ")
            vendor_id = vendors.get(vendor_name)
            if not vendor_id: continue
            
            text = file_path.read_text()
            penalty_pct = 0.0
            grace_days = 0
            
            pct_match = re.search(r"(\d+)%\s+penalty", text)
            if pct_match: penalty_pct = float(pct_match.group(1)) / 100.0
            
            days_match = re.search(r"(\d+)\s+days\s+late", text)
            if days_match: grace_days = int(days_match.group(1))
            
            contract_data.append((vendor_id, text, penalty_pct, grace_days))
        
        conn.executemany("INSERT INTO Contracts VALUES (?, ?, ?, ?)", contract_data)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_db_migrator.py::test_import_contracts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add db_migrator.py
git commit -m "feat: implement contract term extraction"
```

---

### Task 5: Final Migration and Verification

**Files:**
- Modify: `db_migrator.py` (add `main` block)
- Test: `tests/test_db_migrator.py`

- [ ] **Step 1: Implement `main` in `db_migrator.py`**

```python
def run_full_migration():
    db_path = "consolidated_audit.db"
    if os.path.exists(db_path): os.remove(db_path)
    create_schema(db_path)
    migrate_ledger("ap_ledger.db", db_path)
    import_receipts("warehouse_receipts_fy26.csv", db_path)
    import_contracts("contracts", db_path)
    print(f"Migration complete: {db_path}")

if __name__ == "__main__":
    run_full_migration()
```

- [ ] **Step 2: Run migration**

Run: `python3 db_migrator.py`
Expected: "Migration complete: consolidated_audit.db"

- [ ] **Step 3: Verify with SQL query**

Run: `sqlite3 consolidated_audit.db "SELECT COUNT(*) FROM Invoices"`
Expected: A number > 0.

- [ ] **Step 4: Commit**

```bash
git add db_migrator.py
git commit -m "feat: complete full migration script"
```
