import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

INITIAL_ACTIVITIES = copy.deepcopy(activities)


def setup_function():
    # Reset in-memory activity data between tests so tests are isolated.
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup?email=newstudent%40mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    existing_email = activities["Chess Club"]["participants"][0]
    response = client.post(f"/activities/Chess%20Club/signup?email={existing_email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown%20Activity/signup?email=test%40mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    email = activities["Chess Club"]["participants"][0]
    response = client.post(f"/activities/Chess%20Club/unregister?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.post("/activities/Chess%20Club/unregister?email=missing%40mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
