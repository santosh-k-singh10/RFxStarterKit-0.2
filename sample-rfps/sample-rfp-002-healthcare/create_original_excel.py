"""
Script to create Excel file from RFP data for Healthcare RFP
"""
import openpyxl
from openpyxl import Workbook

# Create a new workbook and get the active worksheet
wb = Workbook()
ws = wb.active

# Fix: Check if ws is not None before accessing title
if ws is not None:
    ws.title = "Healthcare RFP Data"
else:
    print("Error: Worksheet is None")

# Save the workbook
wb.save('sample-rfps/sample-rfp-002-healthcare/RFP-2026-HC-002-Cost-Original.xlsx')

# Made with Bob