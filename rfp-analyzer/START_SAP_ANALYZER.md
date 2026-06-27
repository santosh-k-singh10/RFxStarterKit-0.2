# Quick Start Guide - SAP Analyzer

## Start the Application

### Option 1: Using Python directly

Open a terminal/command prompt in the `rfp-analyzer` directory and run:

```bash
cd C:\Agents\BoB-Submission\rfp-analyzer
python sap_analyzer_app.py
```

### Option 2: Using the batch file (Windows)

Double-click: `start_sap_analyzer.bat`

### Option 3: Using the shell script (Mac/Linux)

```bash
chmod +x start_sap_analyzer.sh
./start_sap_analyzer.sh
```

## Access the Application

Once started, the application will be available at:

**http://localhost:8002**

You should see output like:
```
======================================================================
SAP Requirements Mapping Analyzer
======================================================================

Starting server on http://localhost:8002

This is a standalone tool for SAP-specific RFP analysis.
It processes output from the main RFP Analyzer.

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8002
```

## Test It

1. Open your browser to http://localhost:8002
2. Paste some sample requirements:
   ```
   The system shall manage accounts payable
   The system shall support general ledger accounting
   The system shall handle purchase orders
   ```
3. Click "Analyze Requirements"
4. View the SAP module mapping results!

## Stop the Server

Press `Ctrl+C` in the terminal to stop the server.

## Troubleshooting

### Port 8002 already in use?
Edit `sap_analyzer_app.py` and change the port number at the bottom:
```python
uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")  # Changed to 8003
```

### Import errors?
Make sure you're in the correct directory:
```bash
cd C:\Agents\BoB-Submission\rfp-analyzer
```

And that dependencies are installed:
```bash
pip install -r requirements.txt