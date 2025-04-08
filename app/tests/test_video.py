from unittest.mock import patch
import os
import pytest
from fastapi.testclient import TestClient
from app.backend.api import app, video_dir
from app.backend.models import Video as VideoModel
from app.backend.database import SessionLocal

client = TestClient(app)

@pytest.fixture
def sample_video_file(tmp_path):
    """Create a small dummy MP4 file for testing."""
    video_path = tmp_path / "test_video.mp4"
    # Instead of creating a real video, we'll use a mock video file for testing
    # Just a placeholder file for the test
    with open(video_path, "wb") as f:
        f.write(b"dummy video content")
    return open(video_path, "rb")

@patch("app.backend.api.get_video_dimensions", return_value=(320, 240))
def test_upload_video_success(mock_get_video_dimensions, sample_video_file):
    """Test video upload, mocking the video dimensions extraction."""
    response = client.post(
        "/upload-video",
        files={"file": ("test_video.mp4", sample_video_file, "video/mp4")},
        data={"uploader_id": 1},
    )

    sample_video_file.close()
    assert response.status_code == 200
    json_data = response.json()
    assert "filename" in json_data

    filepath = os.path.join(video_dir, json_data["filename"])
    assert os.path.exists(filepath)

    # Check DB record
    with SessionLocal() as db:
        video = db.query(VideoModel).filter_by(filename=json_data["filename"]).first()
        assert video is not None
        assert video.width == 320
        assert video.height == 240

    print("Video upload test passed.")

    # Clean up
    os.remove(filepath)
