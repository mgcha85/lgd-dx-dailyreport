import pytest
from io import BytesIO
from app.models import UserSettings, ClassificationHistory


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_settings_default(client, test_db):
    """Test getting default settings"""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "openai_api_key" in data
    assert data["sheet_name"] == "일보_Worst55"
    assert data["column_name"] == "Issue"


def test_update_settings(client, test_db):
    """Test updating settings"""
    update_data = {
        "openai_api_key": "test-key",
        "openai_base_url": "https://api.test.com/v1",
        "model_name": "gpt-4",
        "sheet_name": "테스트시트",
        "column_name": "TestColumn",
        "few_shot_examples": "예제1\n예제2"
    }
    
    response = client.put("/api/settings", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["openai_api_key"] == "test-key"
    assert data["model_name"] == "gpt-4"
    assert data["sheet_name"] == "테스트시트"


def test_upload_file(client, temp_upload_dir):
    """Test file upload"""
    # Create fake Excel file
    file_content = b"fake excel content"
    files = {"file": ("test.xlsx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    
    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.xlsx"
    assert "file_path" in data


def test_upload_invalid_file(client):
    """Test uploading invalid file type"""
    file_content = b"fake content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400


def test_get_history_empty(client, test_db):
    """Test getting empty history"""
    response = client.get("/api/history")
    assert response.status_code == 200
    assert response.json() == []


def test_get_history_with_data(client, test_db):
    """Test getting history with data"""
    # Add test history
    history = ClassificationHistory(
        filename="test.xlsx",
        file_path="/path/to/test.xlsx",
        sheet_name="일보_Worst55",
        column_name="Issue",
        status="completed",
        total_rows=10,
        processed_rows=8,
        failed_rows=2
    )
    test_db.add(history)
    test_db.commit()
    
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "test.xlsx"
    assert data[0]["status"] == "completed"


def test_get_history_by_id(client, test_db):
    """Test getting history by ID"""
    history = ClassificationHistory(
        filename="test.xlsx",
        file_path="/path/to/test.xlsx",
        sheet_name="일보_Worst55",
        column_name="Issue",
        status="completed"
    )
    test_db.add(history)
    test_db.commit()
    test_db.refresh(history)
    
    response = client.get(f"/api/history/{history.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.xlsx"


def test_get_history_by_id_not_found(client, test_db):
    """Test getting non-existent history"""
    response = client.get("/api/history/9999")
    assert response.status_code == 404
