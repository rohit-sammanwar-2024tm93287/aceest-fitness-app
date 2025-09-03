import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from app import app, FitnessTracker

class TestFitnessTracker:
    """Test cases for the FitnessTracker class"""

    def setup_method(self):
        """Setup method to create a temporary file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.tracker = FitnessTracker(data_file=self.temp_file.name)

    def teardown_method(self):
        """Cleanup method to remove temporary file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_add_workout_success(self):
        """Test successful workout addition"""
        success, message = self.tracker.add_workout("Push-ups", "30")
        assert success is True
        assert "Push-ups" in message
        assert len(self.tracker.get_workouts()) == 1
        assert self.tracker.get_workouts()[0]["workout"] == "Push-ups"
        assert self.tracker.get_workouts()[0]["duration"] == 30

    def test_add_workout_empty_name(self):
        """Test adding workout with empty name"""
        success, message = self.tracker.add_workout("", "30")
        assert success is False
        assert "Please enter both" in message
        assert len(self.tracker.get_workouts()) == 0

    def test_add_workout_empty_duration(self):
        """Test adding workout with empty duration"""
        success, message = self.tracker.add_workout("Running", "")
        assert success is False
        assert "Please enter both" in message
        assert len(self.tracker.get_workouts()) == 0

    def test_add_workout_invalid_duration(self):
        """Test adding workout with invalid duration"""
        success, message = self.tracker.add_workout("Swimming", "abc")
        assert success is False
        assert "must be a valid number" in message
        assert len(self.tracker.get_workouts()) == 0

    def test_add_workout_negative_duration(self):
        """Test adding workout with negative duration"""
        success, message = self.tracker.add_workout("Cycling", "-10")
        assert success is False
        assert "must be a positive number" in message
        assert len(self.tracker.get_workouts()) == 0

    def test_add_workout_zero_duration(self):
        """Test adding workout with zero duration"""
        success, message = self.tracker.add_workout("Yoga", "0")
        assert success is False
        assert "must be a positive number" in message
        assert len(self.tracker.get_workouts()) == 0

    def test_multiple_workouts(self):
        """Test adding multiple workouts"""
        self.tracker.add_workout("Push-ups", "30")
        self.tracker.add_workout("Running", "45")
        self.tracker.add_workout("Squats", "25")

        workouts = self.tracker.get_workouts()
        assert len(workouts) == 3
        assert workouts[0]["workout"] == "Push-ups"
        assert workouts[1]["workout"] == "Running"
        assert workouts[2]["workout"] == "Squats"

    def test_get_total_duration(self):
        """Test total duration calculation"""
        self.tracker.add_workout("Push-ups", "30")
        self.tracker.add_workout("Running", "45")
        self.tracker.add_workout("Squats", "25")

        total_duration = self.tracker.get_total_duration()
        assert total_duration == 100

    def test_get_total_duration_empty(self):
        """Test total duration with no workouts"""
        total_duration = self.tracker.get_total_duration()
        assert total_duration == 0

    def test_reset_workouts(self):
        """Test resetting all workouts"""
        # Add some workouts first
        self.tracker.add_workout("Push-ups", "30")
        self.tracker.add_workout("Running", "45")
        assert len(self.tracker.get_workouts()) == 2

        # Reset workouts
        success, message = self.tracker.reset_workouts()
        assert success is True
        assert "reset successfully" in message
        assert len(self.tracker.get_workouts()) == 0
        assert self.tracker.get_total_duration() == 0

    def test_data_persistence(self):
        """Test that data persists to file"""
        # Add workout and save
        self.tracker.add_workout("Push-ups", "30")

        # Create new tracker instance with same file
        new_tracker = FitnessTracker(data_file=self.temp_file.name)
        workouts = new_tracker.get_workouts()

        assert len(workouts) == 1
        assert workouts[0]["workout"] == "Push-ups"
        assert workouts[0]["duration"] == 30


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


class TestFlaskApp:
    """Test cases for the Flask web application"""

    def test_home_page(self, client):
        """Test the home page loads correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ACEest Fitness and Gym' in response.data
        assert b'Add New Workout' in response.data

    def test_add_workout_form_success(self, client):
        """Test adding workout through web form successfully"""
        with patch('app.tracker.add_workout') as mock_add:
            mock_add.return_value = (True, "Push-ups added successfully!")

            response = client.post('/add_workout', data={
                'workout_name': 'Push-ups',
                'duration': '30'
            }, follow_redirects=True)

            assert response.status_code == 200
            mock_add.assert_called_once_with('Push-ups', '30')

    def test_add_workout_form_validation(self, client):
        """Test form validation for invalid input"""
        with patch('app.tracker.add_workout') as mock_add:
            mock_add.return_value = (False, "Please enter both workout and duration.")

            response = client.post('/add_workout', data={
                'workout_name': '',
                'duration': '30'
            }, follow_redirects=True)

            assert response.status_code == 200
            mock_add.assert_called_once_with('', '30')

    def test_reset_workouts_form(self, client):
        """Test resetting workouts through web form"""
        with patch('app.tracker.reset_workouts') as mock_reset:
            mock_reset.return_value = (True, "All workouts have been reset successfully!")

            response = client.post('/reset_workouts', follow_redirects=True)
            assert response.status_code == 200
            mock_reset.assert_called_once()

    def test_api_get_workouts(self, client):
        """Test API endpoint for getting workouts"""
        test_workouts = [{"workout": "Push-ups", "duration": 30, "id": 1}]

        with patch('app.tracker.get_workouts') as mock_get_workouts, \
                patch('app.tracker.get_total_duration') as mock_get_total:
            mock_get_workouts.return_value = test_workouts
            mock_get_total.return_value = 30

            response = client.get('/api/workouts')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'workouts' in data
            assert 'total_duration' in data
            assert data['workouts'] == test_workouts
            assert data['total_duration'] == 30

    def test_api_add_workout_success(self, client):
        """Test API endpoint for adding workouts successfully"""
        test_workouts = [{"workout": "Running", "duration": 45, "id": 1}]

        with patch('app.tracker.add_workout') as mock_add, \
                patch('app.tracker.get_workouts') as mock_get:
            mock_add.return_value = (True, "Running added successfully!")
            mock_get.return_value = test_workouts

            response = client.post('/api/workouts',
                                   json={'workout_name': 'Running', 'duration': 45},
                                   content_type='application/json')

            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'message' in data
            assert 'workouts' in data
            mock_add.assert_called_once_with('Running', '45')

    def test_api_add_workout_invalid(self, client):
        """Test API endpoint with invalid data"""
        with patch('app.tracker.add_workout') as mock_add:
            mock_add.return_value = (False, "Please enter both workout and duration.")

            response = client.post('/api/workouts',
                                   json={'workout_name': '', 'duration': 'abc'},
                                   content_type='application/json')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'ACEest Fitness' in data['service']


if __name__ == '__main__':
    pytest.main(['-v'])