from fastapi.testclient import TestClient
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


