#Step 21: Add a test for the get-parameters endpoint
from fastapi.testclient import TestClient
from main import app, db  # the FastAPI app is named 'app' chane it to EPF_API
from unittest.mock import MagicMock
import os

# Mock the Firestore client if testing
if "FIREBASE_APPLICATION_CREDENTIALS" not in os.environ:
    db.Client = MagicMock()

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_get_parameters():
    response = client.get("/v1/get-parameters")
    assert response.status_code == 200
    # Add additional assertions based on the expected response for the get-parameters endpoint

def test_update_parameters():
    # Implement a test for the update-parameters endpoint
    pass

# Add more test if i have more motivation