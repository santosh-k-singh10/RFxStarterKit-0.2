# Test Suite for RFP Analyzer

This directory contains the test suite for the RFP Analyzer architecture generation system.

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_models.py -v
```

### Run tests with coverage (if pytest-cov is installed)
```bash
pytest tests/ --cov=architecture_designer --cov=router --cov-report=html
```

### Run only fast tests (exclude slow/integration tests)
```bash
pytest tests/ -v -m "not slow and not integration"
```

## Test Structure

- `conftest.py` - Shared fixtures and pytest configuration
- `test_models.py` - Tests for data models (EnrichedRequirement, Component, etc.)
- `test_api.py` - Tests for FastAPI endpoints (to be added)
- `test_enricher.py` - Tests for requirement enrichment (to be added)
- `test_exporters.py` - Tests for export functionality (to be added)

## Test Markers

- `@pytest.mark.integration` - Tests that require external services
- `@pytest.mark.slow` - Tests that take >5 seconds
- `@pytest.mark.api` - Tests for API endpoints

## Fixtures

### Available Fixtures (from conftest.py)

- `mock_llm_response` - Mock LLM API response
- `mock_llm_client` - Mocked LLM client for testing without API calls
- `sample_requirements` - Sample markdown requirements
- `sample_enriched_modules` - Sample enriched modules for Phase 1.5 testing

## Writing New Tests

Example test structure:

```python
def test_my_feature(sample_requirements):
    """Test description."""
    # Arrange
    input_data = sample_requirements
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result is not None
    assert result.some_property == expected_value
```

## Current Test Coverage

- ✅ Data models (EnrichedRequirement, Component, StoryPointRange, etc.)
- ⏳ API endpoints (to be added)
- ⏳ Enrichment logic (to be added)
- ⏳ Export functionality (to be added)

## Dependencies

Required packages:
```bash
pip install pytest pytest-asyncio
```

Optional for coverage:
```bash
pip install pytest-cov