from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    
    # Test that we have activities and they have the required fields
    activities = response.json()
    assert len(activities) > 0
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_for_activity():
    """Test the signup endpoint"""
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"
    
    # First, try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify the student was added by checking activities
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]
    
    # Try to sign up the same student again (should fail)
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_from_activity():
    """Test the unregister endpoint"""
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"
    
    # First, sign up a student
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Then unregister them
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify the student was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]
    
    # Try to unregister again (should fail)
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_nonexistent_activity():
    """Test handling of non-existent activities"""
    activity_name = "NonExistentClub"
    email = "test_student@mergington.edu"
    
    # Try to sign up for non-existent activity
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    
    # Try to unregister from non-existent activity
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]