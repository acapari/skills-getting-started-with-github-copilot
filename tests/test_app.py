"""
Tests for the FastAPI activities application.
"""

import pytest


def test_root_redirect(client):
    """Test that the root path redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check that each activity has the required fields
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_name, str)
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_get_activities_contains_basketball(client):
    """Test that Basketball activity is in the activities list"""
    response = client.get("/activities")
    activities = response.json()
    
    assert "Basketball" in activities
    assert activities["Basketball"]["description"] == "Team sport focusing on skills, strategy, and fitness"
    assert activities["Basketball"]["max_participants"] == 15


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    email = "newstudent@mergington.edu"
    activity = "Basketball"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity in result["message"]


def test_signup_for_activity_already_registered(client):
    """Test that signup fails if student is already registered"""
    email = "alex@mergington.edu"  # Already in Basketball
    activity = "Basketball"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"].lower()


def test_signup_for_nonexistent_activity(client):
    """Test that signup fails if activity doesn't exist"""
    email = "newstudent@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()


def test_unregister_from_activity_success(client):
    """Test successful unregistration from an activity"""
    email = "alex@mergington.edu"  # Already in Basketball
    activity = "Basketball"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]


def test_unregister_from_activity_not_registered(client):
    """Test that unregister fails if student is not registered"""
    email = "notregistered@mergington.edu"
    activity = "Basketball"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"].lower()


def test_unregister_from_nonexistent_activity(client):
    """Test that unregister fails if activity doesn't exist"""
    email = "alex@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()


def test_signup_and_verify_participant_added(client):
    """Test that signup actually adds the participant to the activity"""
    email = "testuser@mergington.edu"
    activity = "Tennis Club"
    
    # Signup
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity]["participants"]


def test_unregister_and_verify_participant_removed(client):
    """Test that unregister actually removes the participant from the activity"""
    email = "sarah@mergington.edu"  # Already in Tennis Club
    activity = "Tennis Club"
    
    # Verify participant exists
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity]["participants"]
    
    # Unregister
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity]["participants"]
