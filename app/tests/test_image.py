import os
import pytest
from fastapi.testclient import TestClient
from app.backend.api import app, image_dir
from app.backend.database import SessionLocal
from app.backend.models import Image

from PIL import Image
from io import BytesIO

client = TestClient(app)

def create_test_image():
    """Creates a simple in-memory image for upload testing."""
    img = Image.new("RGB", (100, 100), color="red")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def test_upload_image():
    # Create test image
    image_data = create_test_image()

    # Send POST request
    response = client.post(
        "/upload",
        files={"file": ("test.png", image_data, "image/png")},
        data={"uploader_id": 1},
    )

    assert response.status_code == 200
    json_data = response.json()

    # Check keys exist
    assert "filename" in json_data

    # Confirm file is saved
    filepath = os.path.join(image_dir, json_data["filename"])
    assert os.path.exists(filepath)

    print("Image upload test passed.")

    # Clean up test image file (optional)
    os.remove(filepath)
