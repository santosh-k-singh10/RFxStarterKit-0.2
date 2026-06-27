"""Test script for Excel export functionality."""
import requests
import json

# Test data
data = {
    "requirements": [
        "The system shall manage accounts payable including invoice processing",
        "The system shall support general ledger accounting with real-time postings",
        "The system shall handle purchase order creation and goods receipt",
        "The system shall support sales order management",
        "The system shall provide production planning capabilities"
    ]
}

print("Testing Excel export API...")
print(f"Sending {len(data['requirements'])} requirements")

try:
    # Call the API
    response = requests.post(
        'http://localhost:8002/api/export-excel',
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        # Save the file
        filename = 'SAP_Analysis_Test.xlsx'
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ SUCCESS! Excel file saved as: {filename}")
        print(f"File size: {len(response.content)} bytes")
    else:
        print(f"❌ ERROR: Status code {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")