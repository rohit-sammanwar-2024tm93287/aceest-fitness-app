from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

class FitnessTracker:
    def __init__(self, data_file='workouts.json'):
        self.data_file = data_file
        self.workouts = self.load_workouts()

    def load_workouts(self):
        """Load workouts from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_workouts(self):
        """Save workouts to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.workouts, f, indent=2)

    def add_workout(self, workout_name, duration):
        """Add a new workout"""
        if not workout_name or not duration:
            return False, "Please enter both workout name and duration."

        try:
            duration_int = int(duration)
            if duration_int <= 0:
                return False, "Duration must be a positive number."

            self.workouts.append({
                "workout": workout_name,
                "duration": duration_int,
                "id": len(self.workouts) + 1
            })
            self.save_workouts()
            return True, f"'{workout_name}' added successfully!"
        except ValueError:
            return False, "Duration must be a valid number."

    def get_workouts(self):
        """Get all workouts"""
        return self.workouts

    def reset_workouts(self):
        """Reset all workouts"""
        self.workouts = []
        self.save_workouts()
        return True, "All workouts have been reset successfully!"

    def get_total_duration(self):
        """Get total workout duration"""
        return sum(workout['duration'] for workout in self.workouts)

# Initialize fitness tracker
tracker = FitnessTracker()

@app.route('/')
def index():
    """Home page"""
    workouts = tracker.get_workouts()
    total_duration = tracker.get_total_duration()
    return render_template('index.html', workouts=workouts, total_duration=total_duration)

@app.route('/add_workout', methods=['POST'])
def add_workout():
    """Add a new workout"""
    workout_name = request.form.get('workout_name', '').strip()
    duration = request.form.get('duration', '').strip()

    success, message = tracker.add_workout(workout_name, duration)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('index'))

@app.route('/reset_workouts', methods=['POST'])
def reset_workouts():
    """Reset all workouts"""
    success, message = tracker.reset_workouts()
    flash(message, 'success' if success else 'error')
    return redirect(url_for('index'))

@app.route('/api/workouts', methods=['GET'])
def api_get_workouts():
    """API endpoint to get workouts as JSON"""
    return jsonify({
        'workouts': tracker.get_workouts(),
        'total_duration': tracker.get_total_duration()
    })

@app.route('/api/workouts', methods=['POST'])
def api_add_workout():
    """API endpoint to add workout"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    workout_name = data.get('workout_name', '').strip()
    duration = data.get('duration', '')

    success, message = tracker.add_workout(workout_name, str(duration))

    if success:
        return jsonify({'message': message, 'workouts': tracker.get_workouts()}), 201
    else:
        return jsonify({'error': message}), 400

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'ACEest Fitness Tracker'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)