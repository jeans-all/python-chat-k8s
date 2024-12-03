from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app

client = TestClient(app)

# def test_read_root():
#     """
#     Test if root endpoint returns correct response
#     """
#     # response = client.get("/")
#     # print(response)
#     # assert response.status_code == 200

#     print("\nAvailable routes:")
#     for route in app.routes:
#         print(f"- {route.path} [{route.methods}]")
    
#     # Make the request
#     response = client.get("/")
    
#     # Debug: Print response details
#     print(f"\nResponse status: {response.status_code}")
#     print(f"Response headers: {response.headers}")
#     print(f"Response content: {response.content[:200]}...")  # First 200 chars
    
#     assert response.status_code == 200
def test_read_root():
    # Debug: Print all available routes
    print("\nAvailable routes:")
    for route in app.routes:
        if hasattr(route, 'endpoint') and route.endpoint.__name__ == 'websocket_endpoint':
            print(f"- {route.path} [WebSocket]")
        else:
            print(f"- {route.path} {[m for m in route.methods]}")
    
    # Make the request
    response = client.get("/")
    
    # Debug: Print response details
    print(f"\nResponse status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.content[:200]}...")  # First 200 chars
    
    assert response.status_code == 200
    
def test_health_check():
    """
    Test if health endpoint returns correct status
    """

    # response = client.get("/health")
    # assert response.status_code == 200
    # assert response.json() == {"status": "healthy"}


    print(f"\nHealth check response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}