import requests
import json

r = requests.get('http://localhost:8000/openapi.json')
paths = list(r.json()['paths'].keys())
print('Total paths:', len(paths))
print('\nAll paths:')
for p in sorted(paths):
    print(f'  {p}')

print('\nGSE-related paths:')
gse_paths = [p for p in paths if 'gse' in p.lower()]
for p in gse_paths:
    print(f'  {p}')

# Made with Bob
