import json
import os
from audit_agent import detect_anomalies

def test_detect_anomalies_structure():
    # Ensure the database exists for the test
    # The database consolidated_audit.db should already exist from Task 1
    assert os.path.exists("consolidated_audit.db"), "consolidated_audit.db must exist for tests"
    
    result_str = detect_anomalies()
    result = json.loads(result_str)
    
    assert isinstance(result, dict)
    assert "duplicate_invoices" in result
    assert "ghost_receipts" in result
    assert "amount_outliers" in result
    
    # Check that they are lists
    assert isinstance(result["duplicate_invoices"], list)
    assert isinstance(result["ghost_receipts"], list)
    assert isinstance(result["amount_outliers"], list)

def test_detect_anomalies_logic():
    # This test assumes the migration was successful and data is present
    result_str = detect_anomalies()
    result = json.loads(result_str)
    
    # We expect some data to be present if the migration worked
    # For now, we just verify the keys and that we can call it without error
    # If we knew specific anomalies in the seed data, we could assert them here
    print(f"\nDetected {len(result['duplicate_invoices'])} duplicate invoices")
    print(f"Detected {len(result['ghost_receipts'])} ghost receipts")
    print(f"Detected {len(result['amount_outliers'])} amount outliers")
    
    # Ensure no error was returned
    assert "error" not in result
