# Test Fixtures

This directory contains test fixtures and sample data for testing.

## Structure

```
fixtures/
├── sample_rfp.txt          # Sample RFP document (text)
├── sample_requirements.md  # Sample requirements document
└── README.md              # This file
```

## Usage

Fixtures can be accessed in tests using the `test_fixtures_path` fixture:

```python
def test_with_fixture(test_fixtures_path):
    sample_file = test_fixtures_path / "sample_rfp.txt"
    content = sample_file.read_text()
    # ... test logic
```

## Adding New Fixtures

When adding new test fixtures:

1. Place files in this directory
2. Use descriptive names
3. Document the fixture purpose here
4. Keep files small (< 1MB)
5. Do not include sensitive data