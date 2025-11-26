"""
Pytest configuration and fixtures for GraphRAG tests.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Create a FastAPI test client.

    Returns:
        TestClient instance for testing API endpoints
    """
    return TestClient(app)


@pytest.fixture
def sample_local_query() -> dict[str, str]:
    """
    Sample query request for testing.

    Returns:
        Dictionary with sample query data
    """
    return {
        "question": "What should I monitor when treating diabetes and how often?",
        "method": "local",
    }


@pytest.fixture
def sample_global_query() -> dict[str, str]:
    """
    Sample global request for testing.

    Returns:
        Dictionary with sample query data
    """
    return {
        "question": "What are the most important steps in treating diabetes",
        "method": "global",
    }


@pytest.fixture
def sample_guideline_text() -> str:
    """
    Sample clinical guideline text for testing.

    Returns:
        String containing sample guideline content
    """
    return """
    Diabetes Treatment Guidelines:
    1. Monitor blood glucose levels regularly
    2. Maintain HbA1c below 7% for most adults
    3. Consider lifestyle modifications first
    4. Prescribe metformin as first-line therapy
    5. Adjust medications based on individual response
    """
