"""
Pytest configuration and shared fixtures for RFxStarterKit tests.
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Return the project root directory path."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def sample_rfps_path(project_root_path: Path) -> Path:
    """Return the sample RFPs directory path."""
    return project_root_path / "sample-rfps"


@pytest.fixture(scope="session")
def test_fixtures_path() -> Path:
    """Return the test fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary output directory for tests."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(exist_ok=True)
    yield output_dir


@pytest.fixture(scope="session")
def mock_env_vars() -> dict[str, str]:
    """Return mock environment variables for testing."""
    return {
        "OPENAI_API_KEY": "sk-test-key",
        "ANTHROPIC_API_KEY": "sk-ant-test-key",
        "LOG_LEVEL": "DEBUG",
        "MIN_CONFIDENCE": "0.0",
    }


@pytest.fixture(autouse=True)
def setup_test_env(mock_env_vars: dict[str, str], monkeypatch) -> None:
    """Automatically set up test environment variables for all tests."""
    for key, value in mock_env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def sample_requirements_text() -> str:
    """Return sample requirements text for testing."""
    return """
    # Functional Requirements
    
    ## FR-001: User Authentication
    The system must provide secure user authentication using OAuth 2.0.
    Priority: MUST
    
    ## FR-002: Document Upload
    The system should support uploading documents in PDF and DOCX formats.
    Priority: SHOULD
    
    # Non-Functional Requirements
    
    ## NFR-001: Performance
    The system must process documents within 5 minutes for files up to 100 pages.
    Priority: MUST
    
    ## NFR-002: Scalability
    The system should handle up to 1000 concurrent users.
    Priority: SHOULD
    """


@pytest.fixture
def sample_rfp_metadata() -> dict:
    """Return sample RFP metadata for testing."""
    return {
        "title": "Test RFP Analysis",
        "file_name": "test_rfp.pdf",
        "source": "test",
        "date": "2026-07-03",
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: mark test as requiring real API keys"
    )