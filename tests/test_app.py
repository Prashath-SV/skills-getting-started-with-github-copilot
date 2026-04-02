"""
Tests for the Mergington High School API
"""

from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    initial = deepcopy(activities)
    yield
    activities.clear()
    activities.update(initial)


def test_root_redirect(client=client):
    # Arrange
    # client fixture is ready

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client=client):
    # Arrange
    # baseline activities setup via fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert len(data) == 10


def test_signup_for_existing_activity(client=client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_student_raises_400(client=client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_raises_404(client=client):
    # Arrange
    activity_name = "NonExistent"
    email = "x@x.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success(client=client):
    # Arrange
    activity_name = "Debate Club"
    participant_email = "alex@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{participant_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_missing_participant_raises_404(client=client):
    # Arrange
    activity_name = "Debate Club"
    participant_email = "missing@x.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{participant_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_unknown_activity_raises_404(client=client):
    # Arrange
    activity_name = "Unknown Club"
    participant_email = "student@x.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{participant_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
