import sqlite3
import csv
from datetime import datetime

def create_schema(db_path):
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE Vendors (Vendor_ID TEXT PRIMARY KEY, Vendor_Name TEXT, GSTIN TEXT, Address TEXT);
            CREATE TABLE Invoices (Invoice_ID TEXT PRIMARY KEY, Vendor_ID TEXT, Amount REAL, Invoice_Date TEXT, Status TEXT, FOREIGN KEY(Vendor_ID) REFERENCES Vendors(Vendor_ID));
            CREATE TABLE Payments (Payment_ID TEXT PRIMARY KEY, Invoice_ID TEXT, Amount REAL, Payment_Date TEXT, FOREIGN KEY(Invoice_ID) REFERENCES Invoices(Invoice_ID));
            CREATE TABLE Receipts (Receipt_ID TEXT PRIMARY KEY, Vendor_ID TEXT, Expected_Delivery TEXT, Actual_Delivery TEXT, Quality_Status TEXT, Days_Late INTEGER, FOREIGN KEY(Vendor_ID) REFERENCES Vendors(Vendor_ID));
            CREATE TABLE Contracts (Vendor_ID TEXT PRIMARY KEY, Contract_Text TEXT, Penalty_Percentage REAL, Grace_Period_Days INTEGER, FOREIGN KEY(Vendor_ID) REFERENCES Vendors(Vendor_ID));
        """)

def migrate_ledger(source_path, target_path):
    with sqlite3.connect(target_path) as conn:
        conn.execute(f"ATTACH DATABASE '{source_path}' AS source")
        conn.execute("INSERT INTO Vendors SELECT * FROM source.Vendors")
        conn.execute("INSERT INTO Invoices SELECT * FROM source.Invoices")
        conn.execute("INSERT INTO Payments SELECT * FROM source.Payments")
        conn.commit()

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
