"""
Script to create Excel file from RFP data
"""
import openpyxl
from openpyxl import Workbook

# Example: If you're accessing title from a worksheet or cell
wb = Workbook()
ws = wb.active

# Fix: Check if ws is not None before accessing title
if ws is not None:
    ws.title = "RFP Data"
else:
    print("Error: Worksheet is None")

# Alternative fix: Use getattr with default
# title = getattr(ws, 'title', 'Default Title')

# Save the workbook
wb.save('sample-rfps/sample-rfp-001/RFP-2026-IT-001-Cost-Breakdown.xlsx')

# Made with Bob
