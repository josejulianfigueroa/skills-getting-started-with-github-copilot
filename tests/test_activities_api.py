from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)

    with TestClient(app) as test_client:
        yield test_client

    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_data(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert activity_name in response.json()
    assert "participants" in response.json()[activity_name]


def test_signup_adds_participant(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )
    participants = client.get("/activities").json()["Chess Club"]["participants"]

    # Assert
    assert response.status_code == 200
    assert email in participants


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )
    participants = client.get("/activities").json()["Chess Club"]["participants"]

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert participants.count(email) == 1


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_path = "/activities/Unknown%20Club/signup"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        activity_path,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )
    participants = client.get("/activities").json()["Chess Club"]["participants"]

    # Assert
    assert response.status_code == 200
    assert email not in participants


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_path = "/activities/Unknown%20Club/signup"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        activity_path,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"