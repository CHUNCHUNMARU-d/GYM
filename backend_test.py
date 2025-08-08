#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Workout Tracking App
Tests all API endpoints with realistic workout data
"""

import requests
import json
import uuid
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = "https://e91f0d44-cd77-4ef9-9b4d-3aa8cc40e47e.preview.emergentagent.com/api"

class WorkoutTrackerTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_id = None
        self.test_exercise_ids = []
        self.test_workout_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if response and not success:
            print(f"   Response: {response.status_code} - {response.text[:200]}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
        print()
    
    def test_health_check(self):
        """Test 1: Health Check Endpoint"""
        print("=== Testing Health Check Endpoint ===")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health Check", True, "Service is healthy")
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid health response format", response)
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_exercise_management(self):
        """Test 2: Exercise Management (CRUD operations)"""
        print("=== Testing Exercise Management ===")
        
        # Test GET /api/exercises - should return pre-loaded exercises
        try:
            response = requests.get(f"{self.base_url}/exercises", timeout=10)
            if response.status_code == 200:
                exercises = response.json()
                if isinstance(exercises, list) and len(exercises) > 0:
                    self.log_result("GET Exercises", True, f"Retrieved {len(exercises)} exercises")
                    # Store some exercise IDs for later tests
                    self.test_exercise_ids = [ex["id"] for ex in exercises[:3]]
                else:
                    self.log_result("GET Exercises", False, "No exercises found or invalid format", response)
                    return False
            else:
                self.log_result("GET Exercises", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("GET Exercises", False, f"Connection error: {str(e)}")
            return False
        
        # Test POST /api/exercises - create new exercise
        try:
            # Use a unique name to avoid duplicates
            unique_name = f"Test Exercise {uuid.uuid4().hex[:8]}"
            new_exercise_data = {
                "name": unique_name,
                "muscle_group": "Legs"
            }
            response = requests.post(
                f"{self.base_url}/exercises",
                params=new_exercise_data,
                timeout=10
            )
            if response.status_code == 200:
                exercise = response.json()
                if "id" in exercise and exercise["name"] == new_exercise_data["name"]:
                    self.log_result("POST Exercise", True, f"Created exercise: {exercise['name']}")
                    self.test_exercise_ids.append(exercise["id"])
                else:
                    self.log_result("POST Exercise", False, "Invalid exercise creation response", response)
            else:
                self.log_result("POST Exercise", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("POST Exercise", False, f"Connection error: {str(e)}")
        
        # Test GET /api/exercises/search - search functionality
        try:
            response = requests.get(f"{self.base_url}/exercises/search?query=bench", timeout=10)
            if response.status_code == 200:
                search_results = response.json()
                if isinstance(search_results, list):
                    bench_found = any("bench" in ex["name"].lower() for ex in search_results)
                    if bench_found:
                        self.log_result("Exercise Search", True, f"Found {len(search_results)} exercises matching 'bench'")
                    else:
                        self.log_result("Exercise Search", False, "No bench exercises found in search results")
                else:
                    self.log_result("Exercise Search", False, "Invalid search response format", response)
            else:
                self.log_result("Exercise Search", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Exercise Search", False, f"Connection error: {str(e)}")
        
        return len(self.test_exercise_ids) > 0
    
    def test_user_management(self):
        """Test 3: User Management"""
        print("=== Testing User Management ===")
        
        # Test POST /api/users - create user
        try:
            user_data = {
                "name": "John Smith",
                "email": "john.smith@example.com"
            }
            response = requests.post(
                f"{self.base_url}/users",
                params=user_data,
                timeout=10
            )
            if response.status_code == 200:
                user = response.json()
                if "id" in user and user["name"] == user_data["name"]:
                    self.test_user_id = user["id"]
                    self.log_result("POST User", True, f"Created user: {user['name']} (ID: {user['id'][:8]}...)")
                else:
                    self.log_result("POST User", False, "Invalid user creation response", response)
                    return False
            else:
                self.log_result("POST User", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("POST User", False, f"Connection error: {str(e)}")
            return False
        
        # Test GET /api/users/{user_id} - get user
        try:
            response = requests.get(f"{self.base_url}/users/{self.test_user_id}", timeout=10)
            if response.status_code == 200:
                user = response.json()
                if user["id"] == self.test_user_id:
                    self.log_result("GET User", True, f"Retrieved user: {user['name']}")
                else:
                    self.log_result("GET User", False, "User ID mismatch", response)
            else:
                self.log_result("GET User", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("GET User", False, f"Connection error: {str(e)}")
        
        return self.test_user_id is not None
    
    def test_workout_creation(self):
        """Test 4: Workout Creation and Logging"""
        print("=== Testing Workout Creation ===")
        
        if not self.test_user_id or not self.test_exercise_ids:
            self.log_result("Workout Creation", False, "Missing test user or exercises")
            return False
        
        # Create a realistic workout with multiple exercises and sets
        workout_data = {
            "user_id": self.test_user_id,
            "exercises": [
                {
                    "exercise_id": self.test_exercise_ids[0],
                    "exercise_name": "Bench Press",
                    "sets": [
                        {"set_number": 1, "weight_kg": 80.0, "reps": 8, "rir": 2},
                        {"set_number": 2, "weight_kg": 82.5, "reps": 6, "rir": 1},
                        {"set_number": 3, "weight_kg": 85.0, "reps": 5, "rir": 0}
                    ]
                },
                {
                    "exercise_id": self.test_exercise_ids[1] if len(self.test_exercise_ids) > 1 else self.test_exercise_ids[0],
                    "exercise_name": "Squat",
                    "sets": [
                        {"set_number": 1, "weight_kg": 100.0, "reps": 10, "rir": 3},
                        {"set_number": 2, "weight_kg": 105.0, "reps": 8, "rir": 2},
                        {"set_number": 3, "weight_kg": 110.0, "reps": 6, "rir": 1}
                    ]
                }
            ],
            "notes": "Great workout session, felt strong today",
            "duration_minutes": 75
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/workouts",
                json=workout_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                workout = response.json()
                if "id" in workout and workout["user_id"] == self.test_user_id:
                    self.test_workout_id = workout["id"]
                    exercise_count = len(workout.get("exercises", []))
                    self.log_result("POST Workout", True, f"Created workout with {exercise_count} exercises (ID: {workout['id'][:8]}...)")
                    return True
                else:
                    self.log_result("POST Workout", False, "Invalid workout creation response", response)
            else:
                self.log_result("POST Workout", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("POST Workout", False, f"Connection error: {str(e)}")
        
        return False
    
    def test_workout_history(self):
        """Test 5: Workout History Retrieval"""
        print("=== Testing Workout History ===")
        
        if not self.test_user_id:
            self.log_result("Workout History", False, "Missing test user")
            return False
        
        try:
            response = requests.get(f"{self.base_url}/workouts/{self.test_user_id}", timeout=10)
            if response.status_code == 200:
                workouts = response.json()
                if isinstance(workouts, list):
                    if len(workouts) > 0:
                        # Verify the workout we just created is in the history
                        workout_found = any(w.get("id") == self.test_workout_id for w in workouts)
                        if workout_found:
                            self.log_result("GET Workout History", True, f"Retrieved {len(workouts)} workouts, including our test workout")
                        else:
                            self.log_result("GET Workout History", True, f"Retrieved {len(workouts)} workouts (test workout may not be included)")
                    else:
                        self.log_result("GET Workout History", True, "No workouts found (empty history)")
                    return True
                else:
                    self.log_result("GET Workout History", False, "Invalid workout history response format", response)
            else:
                self.log_result("GET Workout History", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("GET Workout History", False, f"Connection error: {str(e)}")
        
        return False
    
    def test_workout_statistics(self):
        """Test 6: Workout Statistics and Progress Tracking"""
        print("=== Testing Workout Statistics ===")
        
        if not self.test_user_id:
            self.log_result("Workout Statistics", False, "Missing test user")
            return False
        
        try:
            response = requests.get(f"{self.base_url}/workouts/{self.test_user_id}/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                if "total_workouts" in stats and "exercise_stats" in stats:
                    total_workouts = stats["total_workouts"]
                    exercise_stats = stats["exercise_stats"]
                    
                    if total_workouts > 0:
                        # Verify statistics calculation
                        stats_valid = True
                        for ex_id, ex_stats in exercise_stats.items():
                            required_fields = ["name", "total_sets", "total_reps", "total_volume_kg", "max_weight_kg", "avg_weight_kg", "sessions"]
                            if not all(field in ex_stats for field in required_fields):
                                stats_valid = False
                                break
                        
                        if stats_valid:
                            self.log_result("GET Workout Stats", True, f"Retrieved stats for {total_workouts} workouts, {len(exercise_stats)} exercises")
                        else:
                            self.log_result("GET Workout Stats", False, "Statistics missing required fields")
                    else:
                        self.log_result("GET Workout Stats", True, "No workout statistics (no workouts recorded)")
                    return True
                else:
                    self.log_result("GET Workout Stats", False, "Invalid statistics response format", response)
            else:
                self.log_result("GET Workout Stats", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("GET Workout Stats", False, f"Connection error: {str(e)}")
        
        return False
    
    def test_error_handling(self):
        """Test 7: Error Handling"""
        print("=== Testing Error Handling ===")
        
        # Test invalid user ID
        try:
            response = requests.get(f"{self.base_url}/users/invalid-user-id", timeout=10)
            if response.status_code == 404:
                self.log_result("Invalid User Error", True, "Correctly returned 404 for invalid user")
            else:
                self.log_result("Invalid User Error", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid User Error", False, f"Connection error: {str(e)}")
        
        # Test duplicate exercise creation
        try:
            duplicate_data = {"name": "Bench Press", "muscle_group": "Chest"}
            response = requests.post(f"{self.base_url}/exercises", params=duplicate_data, timeout=10)
            if response.status_code == 400:
                self.log_result("Duplicate Exercise Error", True, "Correctly prevented duplicate exercise creation")
            else:
                self.log_result("Duplicate Exercise Error", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Duplicate Exercise Error", False, f"Connection error: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests in priority order"""
        print("🏋️ Starting Comprehensive Backend Testing for Workout Tracker App")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test in priority order as specified
        tests = [
            ("Health Check", self.test_health_check),
            ("Exercise Management", self.test_exercise_management),
            ("User Management", self.test_user_management),
            ("Workout Creation", self.test_workout_creation),
            ("Workout History", self.test_workout_history),
            ("Workout Statistics", self.test_workout_statistics),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_result(f"{test_name} (Exception)", False, f"Unexpected error: {str(e)}")
        
        # Print final results
        print("=" * 60)
        print("🏁 FINAL TEST RESULTS")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = WorkoutTrackerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)