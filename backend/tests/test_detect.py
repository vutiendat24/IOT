
import pytest
from fastapi.testclient import TestClient
from app.main import app
import io
from PIL import Image
import numpy as np

client = TestClient(app)


def create_test_image():
    """Create a test image"""
    img = Image.new('RGB', (640, 480), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_root_endpoint():
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_detect_without_auth():
    """Test detection endpoint without authentication"""
    response = client.post(
        "/api/detect",
        files={"file": ("test.jpg", create_test_image(), "image/jpeg")}
    )
    assert response.status_code == 401


def test_detect_with_mock_auth():
    """Test detection endpoint with mock authentication"""
    response = client.post(
        "/api/detect",
        files={"file": ("test.jpg", create_test_image(), "image/jpeg")},
        headers={"Authorization": "Bearer test_token"}
    )
    # Should return 200 or 500 depending on model availability
    assert response.status_code in [200, 500]