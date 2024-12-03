from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app

client = TestClient(app)

def test_read_root():
    """
    Test if root endpoint returns correct response
    """
    response = client.get("/")
    assert response.status_code == 200

def test_health_check():
    """
    Test if health endpoint returns correct status
    """

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


