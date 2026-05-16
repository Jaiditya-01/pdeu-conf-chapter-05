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
