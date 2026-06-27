import sys
from pathlib import Path

# Add the analyzer directory to the Python path
analyzer_path = Path(__file__).parent / 'rfp-analyzer' / 'analyzer'
sys.path.insert(0, str(analyzer_path))

from web_app import app  # type: ignore[import-untyped]
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.get('/')
print('Status:', response.status_code)
lines = response.text.split('\n')
print(f'Total lines: {len(lines)}')
if len(lines) > 1175:
    print(f'Line 1176: {repr(lines[1175])}')
    print(f'Line 1175: {repr(lines[1174])}')
    print(f'Line 1177: {repr(lines[1176])}')
else:
    print('Not enough lines')

# Made with Bob
