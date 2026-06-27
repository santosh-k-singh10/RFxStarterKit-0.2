"""
tests/conftest.py — shared pytest configuration for RFP Analyzer tests.

This module provides fixtures and configuration for testing the architecture
analysis system without requiring real API keys or making actual API calls.
"""
import os
import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture(autouse=True)
def clear_api_keys(monkeypatch):
    """
    Remove API keys from environment for all tests unless explicitly set.
    This prevents accidental API calls during testing.
    """
    # Clear both IBM and Anthropic keys
    monkeypatch.delenv("IBM_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture
def mock_llm_response():
    """
    Fixture providing a mock LLM response for architecture generation.
    Returns a properly structured response that matches the expected format.
    """
    return {
        "id": "msg_test123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": """```json
{
  "domains": [
    {
      "name": "Identity & Access",
      "requirements": ["User authentication", "Role-based access"],
      "count": 2,
      "color": "blue"
    }
  ],
  "systemContext": {
    "description": "Test system",
    "actors": [
      {"name": "User", "type": "human", "description": "End user"}
    ],
    "integrations": ["OAuth2", "LDAP"]
  },
  "architecture": {
    "recommended": "Modular Monolith",
    "rationale": "Test rationale",
    "keyPrinciples": ["API-first", "Security by design"],
    "alternatives": [],
    "layers": []
  },
  "components": [
    {
      "name": "Auth Service",
      "type": "Backend Service",
      "description": "Authentication service",
      "complexity": "Medium",
      "complexityReason": "OAuth2 integration",
      "complianceImpacted": false,
      "dependencies": [],
      "estimationSignals": ["JWT tokens", "OAuth2 SDK"]
    }
  ],
  "risks": [
    {
      "risk": "Authentication complexity",
      "level": "Medium",
      "mitigation": "Use proven OAuth2 library",
      "refId": "NFR-001"
    }
  ]
}
```"""
            }
        ],
        "model": "test-model",
        "stop_reason": "end_turn",
        "usage": {
            "input_tokens": 1000,
            "output_tokens": 500
        }
    }


@pytest.fixture
def mock_llm_client(mock_llm_response):
    """
    Fixture providing a mocked LLM client that returns test data.
    Use this to test components without making real API calls.
    """
    mock_client = Mock()
    mock_client.create_message = AsyncMock(return_value=mock_llm_response)
    return mock_client


@pytest.fixture
def sample_requirements():
    """Fixture providing sample requirements for testing."""
    return """
# Functional Requirements

## FR-001: User Authentication
**Priority:** MUST | **Confidence:** 95%
Users must be able to register and log in using email/password or OAuth2.

## FR-002: Role-Based Access Control
**Priority:** MUST | **Confidence:** 90%
System must support admin, user, and guest roles with different permissions.

# Non-Functional Requirements

## NFR-001: Performance
**Priority:** MUST | **Confidence:** 85%
System must handle 1000 concurrent users with <2s response time.

## NFR-002: Security
**Priority:** MUST | **Confidence:** 95%
All data must be encrypted at rest and in transit using industry standards.
"""


@pytest.fixture
def sample_enriched_modules():
    """Fixture providing sample enriched modules for testing."""
    return {
        "modules": {
            "identity_access": [
                {
                    "id": "FR-001",
                    "type": "FR",
                    "title": "User Authentication",
                    "description": "Users must be able to register and log in",
                    "priority": "MUST",
                    "confidence": 95,
                    "is_ambiguous": False,
                    "clarification": "",
                    "related_ids": ["FR-002"],
                    "module": "identity_access",
                    "impl_type": "custom_build",
                    "actors": ["customer", "admin"],
                    "dependency_direction": {}
                },
                {
                    "id": "FR-002",
                    "type": "FR",
                    "title": "Role-Based Access Control",
                    "description": "System must support different user roles",
                    "priority": "MUST",
                    "confidence": 90,
                    "is_ambiguous": False,
                    "clarification": "",
                    "related_ids": ["FR-001"],
                    "module": "identity_access",
                    "impl_type": "custom_build",
                    "actors": ["admin"],
                    "dependency_direction": {}
                }
            ],
            "platform_nfrs": [
                {
                    "id": "NFR-001",
                    "type": "NFR",
                    "title": "Performance",
                    "description": "Handle 1000 concurrent users",
                    "priority": "MUST",
                    "confidence": 85,
                    "is_ambiguous": False,
                    "clarification": "",
                    "related_ids": [],
                    "module": "platform_nfrs",
                    "impl_type": "configuration",
                    "actors": ["system"],
                    "dependency_direction": {}
                }
            ]
        },
        "total": 3
    }


def pytest_configure(config):
    """Register custom markers for test categorization."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require external services (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests that take >5 seconds (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "api: marks tests that test API endpoints"
    )

# Made with Bob
