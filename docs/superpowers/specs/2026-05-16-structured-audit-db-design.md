# Design Spec: Structured Audit Consolidation Database

**Date:** 2026-05-16
**Topic:** Database Generation
**Status:** Draft

## 1. Overview
Consolidate financial, delivery, and legal data from multiple sources (SQLite, CSV, Text) into a single, structured SQLite database to empower the Auditor Agent with SQL-driven discrepancy detection.

## 2. Source Data
- **Financial Ledger (`ap_ledger.db`)**: Tables `Vendors`, `Invoices`, `Payments`.
- **Delivery Log (`warehouse_receipts_fy26.csv`)**: CSV data with delivery performance.
- **Legal Contracts (`./contracts/*.txt`)**: Text files containing penalty clauses.

## 3. Target Schema (`consolidated_audit.db`)

### Table: `Vendors`
- `Vendor_ID` (TEXT, PK)
- `Vendor_Name` (TEXT)
- `GSTIN` (TEXT)
- `Address` (TEXT)

### Table: `Invoices`
- `Invoice_ID` (TEXT, PK)
- `Vendor_ID` (TEXT, FK references Vendors.Vendor_ID)
- `Amount` (REAL)
- `Invoice_Date` (TEXT)
- `Status` (TEXT)

### Table: `Payments`
- `Payment_ID` (TEXT, PK)
- `Invoice_ID` (TEXT, FK references Invoices.Invoice_ID)
- `Amount` (REAL)
- `Payment_Date` (TEXT)

### Table: `Receipts`
- `Receipt_ID` (TEXT, PK)
- `Vendor_ID` (TEXT, FK references Vendors.Vendor_ID)
- `Expected_Delivery` (TEXT)
- `Actual_Delivery` (TEXT)
- `Quality_Status` (TEXT)
- `Days_Late` (INTEGER) - *Calculated during import*

### Table: `Contracts`
- `Vendor_ID` (TEXT, PK, FK references Vendors.Vendor_ID)
- `Contract_Text` (TEXT)
- `Penalty_Percentage` (REAL) - *Extracted (e.g., 0.05 for 5%)*
- `Grace_Period_Days` (INTEGER) - *Extracted (e.g., 7 days)*

## 4. Implementation Strategy

### A. Data Migration
1. Create `consolidated_audit.db`.
2. Attach `ap_ledger.db` and copy `Vendors`, `Invoices`, and `Payments` tables.
3. Import `warehouse_receipts_fy26.csv` into the `Receipts` table.
   - Calculate `Days_Late` using the difference between `Actual_Delivery` and `Expected_Delivery`.

### B. Contract Extraction
1. Iterate through all files in `./contracts/`.
2. Map filename (e.g., `Gujarat_Steel_Corp_Contract.txt`) to `Vendor_Name` and then to `Vendor_ID`.
3. Read the text and extract:
   - **Penalty %**: Search for patterns like "5% penalty".
   - **Grace Period**: Search for patterns like "7 days late".
4. Populate the `Contracts` table.

## 5. Success Criteria
- A single database file `consolidated_audit.db` exists.
- All 5 tables are populated with accurate data.
- A sample SQL query can calculate a penalty for a known late delivery.
- The Auditor Agent can be updated to use this single source of truth.

## 6. Constraints
- Must use standard Python libraries (sqlite3, csv, os, re).
- `Days_Late` must handle date parsing correctly (ISO 8601).
