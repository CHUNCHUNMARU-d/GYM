#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Coach-Client Management System
Tests all API endpoints with realistic coach-client data
"""

import requests
import json
import uuid
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = "https://e91f0d44-cd77-4ef9-9b4d-3aa8cc40e47e.preview.emergentagent.com/api"

class CoachClientSystemTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.coach_token = None
        self.client_token = None
        self.test_client_id = None
        self.test_routine_id = None
        self.test_exercise_ids = []
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
    
    def test_authentication_system(self):
        """Test 2: Authentication System (Coach & Client login)"""
        print("=== Testing Authentication System ===")
        
        # Test Coach Login with default credentials
        try:
            coach_data = {
                "username": "coach",
                "password": "coach123"
            }
            response = requests.post(
                f"{self.base_url}/auth/coach/login",
                params=coach_data,
                timeout=10
            )
            if response.status_code == 200:
                auth_data = response.json()
                if "access_token" in auth_data and "user" in auth_data:
                    self.coach_token = auth_data["access_token"]
                    self.log_result("Coach Login", True, f"Coach authenticated: {auth_data['user']['name']}")
                else:
                    self.log_result("Coach Login", False, "Invalid coach login response format", response)
                    return False
            else:
                self.log_result("Coach Login", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Coach Login", False, f"Connection error: {str(e)}")
            return False
        
        # Test Invalid Coach Credentials
        try:
            invalid_data = {
                "username": "coach",
                "password": "wrongpassword"
            }
            response = requests.post(
                f"{self.base_url}/auth/coach/login",
                params=invalid_data,
                timeout=10
            )
            if response.status_code == 401:
                self.log_result("Invalid Coach Credentials", True, "Correctly rejected invalid credentials")
            else:
                self.log_result("Invalid Coach Credentials", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Coach Credentials", False, f"Connection error: {str(e)}")
        
        return self.coach_token is not None
    
    def test_coach_dashboard_client_management(self):
        """Test 3: Coach Dashboard and Client Management"""
        print("=== Testing Coach Dashboard and Client Management ===")
        
        if not self.coach_token:
            self.log_result("Coach Dashboard", False, "No coach token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.coach_token}"}
        
        # Test Coach Dashboard
        try:
            response = requests.get(f"{self.base_url}/coach/dashboard", headers=headers, timeout=10)
            if response.status_code == 200:
                dashboard = response.json()
                required_fields = ["coach", "total_clients", "total_workouts_this_week", "active_routines", "clients"]
                if all(field in dashboard for field in required_fields):
                    self.log_result("Coach Dashboard", True, f"Dashboard loaded with {dashboard['total_clients']} clients")
                else:
                    self.log_result("Coach Dashboard", False, "Dashboard missing required fields", response)
            else:
                self.log_result("Coach Dashboard", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Coach Dashboard", False, f"Connection error: {str(e)}")
        
        # Test Create Client
        try:
            client_data = {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@example.com"
            }
            response = requests.post(
                f"{self.base_url}/coach/clients",
                params=client_data,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                client = response.json()
                if "id" in client and client["name"] == client_data["name"]:
                    self.test_client_id = client["id"]
                    self.log_result("Create Client", True, f"Created client: {client['name']} (ID: {client['id'][:8]}...)")
                else:
                    self.log_result("Create Client", False, "Invalid client creation response", response)
                    return False
            else:
                self.log_result("Create Client", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Create Client", False, f"Connection error: {str(e)}")
            return False
        
        # Test Get All Clients
        try:
            response = requests.get(f"{self.base_url}/coach/clients", headers=headers, timeout=10)
            if response.status_code == 200:
                clients = response.json()
                if isinstance(clients, list) and len(clients) > 0:
                    client_found = any(c["id"] == self.test_client_id for c in clients)
                    if client_found:
                        self.log_result("Get All Clients", True, f"Retrieved {len(clients)} clients, including our test client")
                    else:
                        self.log_result("Get All Clients", True, f"Retrieved {len(clients)} clients")
                else:
                    self.log_result("Get All Clients", False, "No clients found or invalid format", response)
            else:
                self.log_result("Get All Clients", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get All Clients", False, f"Connection error: {str(e)}")
        
        # Test Client Progress (initially empty)
        if self.test_client_id:
            try:
                response = requests.get(
                    f"{self.base_url}/coach/client/{self.test_client_id}/progress",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    progress = response.json()
                    required_fields = ["client", "workouts", "measurements", "exercise_stats"]
                    if all(field in progress for field in required_fields):
                        self.log_result("Client Progress", True, f"Retrieved progress for client {progress['client']['name']}")
                    else:
                        self.log_result("Client Progress", False, "Progress missing required fields", response)
                else:
                    self.log_result("Client Progress", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("Client Progress", False, f"Connection error: {str(e)}")
        
        return self.test_client_id is not None
    
    def test_exercise_tips_management(self):
        """Test 4: Exercise Tips Management"""
        print("=== Testing Exercise Tips Management ===")
        
        # Test Get All Exercises (should have pre-loaded exercises)
        try:
            response = requests.get(f"{self.base_url}/exercises", timeout=10)
            if response.status_code == 200:
                exercises = response.json()
                if isinstance(exercises, list) and len(exercises) > 0:
                    self.test_exercise_ids = [ex["id"] for ex in exercises[:3]]
                    bench_press = next((ex for ex in exercises if "bench" in ex["name"].lower()), None)
                    if bench_press and bench_press.get("tips"):
                        self.log_result("Get Exercises with Tips", True, f"Retrieved {len(exercises)} exercises with tips")
                    else:
                        self.log_result("Get Exercises with Tips", True, f"Retrieved {len(exercises)} exercises")
                else:
                    self.log_result("Get Exercises with Tips", False, "No exercises found", response)
                    return False
            else:
                self.log_result("Get Exercises with Tips", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Get Exercises with Tips", False, f"Connection error: {str(e)}")
            return False
        
        if not self.coach_token:
            self.log_result("Exercise Management", False, "No coach token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.coach_token}"}
        
        # Test Create New Exercise
        try:
            exercise_data = {
                "name": f"Test Exercise {uuid.uuid4().hex[:8]}",
                "muscle_group": "Core",
                "tips": "Keep your core engaged throughout the movement and breathe steadily."
            }
            response = requests.post(
                f"{self.base_url}/coach/exercises",
                params=exercise_data,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                exercise = response.json()
                if "id" in exercise and exercise["name"] == exercise_data["name"]:
                    self.test_exercise_ids.append(exercise["id"])
                    self.log_result("Create Exercise", True, f"Created exercise: {exercise['name']}")
                else:
                    self.log_result("Create Exercise", False, "Invalid exercise creation response", response)
            else:
                self.log_result("Create Exercise", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Exercise", False, f"Connection error: {str(e)}")
        
        # Test Update Exercise Tips
        if self.test_exercise_ids:
            try:
                new_tips = "Updated form tips: Focus on proper breathing and controlled movement."
                response = requests.put(
                    f"{self.base_url}/coach/exercises/{self.test_exercise_ids[0]}",
                    params={"tips": new_tips},
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    exercise = response.json()
                    if exercise.get("tips") == new_tips:
                        self.log_result("Update Exercise Tips", True, "Successfully updated exercise tips")
                    else:
                        self.log_result("Update Exercise Tips", False, "Tips not updated correctly", response)
                else:
                    self.log_result("Update Exercise Tips", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("Update Exercise Tips", False, f"Connection error: {str(e)}")
        
        return len(self.test_exercise_ids) > 0
    
    def test_routine_creation_assignment(self):
        """Test 5: Routine Creation and Assignment System"""
        print("=== Testing Routine Creation and Assignment ===")
        
        if not self.coach_token or not self.test_client_id or not self.test_exercise_ids:
            self.log_result("Routine Creation", False, "Missing required test data")
            return False
        
        headers = {"Authorization": f"Bearer {self.coach_token}"}
        
        # Test Create Routine
        try:
            routine_data = {
                "name": "Upper Body Strength",
                "exercises": [
                    {
                        "exercise_id": self.test_exercise_ids[0],
                        "exercise_name": "Bench Press",
                        "target_sets": 3,
                        "target_reps": "8-10",
                        "target_weight": 80.0,
                        "rest_seconds": 120
                    },
                    {
                        "exercise_id": self.test_exercise_ids[1] if len(self.test_exercise_ids) > 1 else self.test_exercise_ids[0],
                        "exercise_name": "Overhead Press",
                        "target_sets": 3,
                        "target_reps": "6-8",
                        "target_weight": 50.0,
                        "rest_seconds": 90
                    }
                ],
                "assigned_clients": [self.test_client_id]
            }
            response = requests.post(
                f"{self.base_url}/coach/routines",
                json=routine_data,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                routine = response.json()
                if "id" in routine and routine["name"] == routine_data["name"]:
                    self.test_routine_id = routine["id"]
                    self.log_result("Create Routine", True, f"Created routine: {routine['name']} with {len(routine['exercises'])} exercises")
                else:
                    self.log_result("Create Routine", False, "Invalid routine creation response", response)
                    return False
            else:
                self.log_result("Create Routine", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Create Routine", False, f"Connection error: {str(e)}")
            return False
        
        # Test Get Coach Routines
        try:
            response = requests.get(f"{self.base_url}/coach/routines", headers=headers, timeout=10)
            if response.status_code == 200:
                routines = response.json()
                if isinstance(routines, list):
                    routine_found = any(r["id"] == self.test_routine_id for r in routines)
                    if routine_found:
                        self.log_result("Get Coach Routines", True, f"Retrieved {len(routines)} routines, including our test routine")
                    else:
                        self.log_result("Get Coach Routines", True, f"Retrieved {len(routines)} routines")
                else:
                    self.log_result("Get Coach Routines", False, "Invalid routines response format", response)
            else:
                self.log_result("Get Coach Routines", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Coach Routines", False, f"Connection error: {str(e)}")
        
        # Test Update Routine
        if self.test_routine_id:
            try:
                updated_data = {
                    "name": "Updated Upper Body Strength",
                    "exercises": [
                        {
                            "exercise_id": self.test_exercise_ids[0],
                            "exercise_name": "Bench Press",
                            "target_sets": 4,
                            "target_reps": "6-8",
                            "target_weight": 85.0,
                            "rest_seconds": 150
                        }
                    ],
                    "assigned_clients": [self.test_client_id]
                }
                response = requests.put(
                    f"{self.base_url}/coach/routines/{self.test_routine_id}",
                    json=updated_data,
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    routine = response.json()
                    if routine.get("name") == updated_data["name"]:
                        self.log_result("Update Routine", True, "Successfully updated routine")
                    else:
                        self.log_result("Update Routine", False, "Routine not updated correctly", response)
                else:
                    self.log_result("Update Routine", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("Update Routine", False, f"Connection error: {str(e)}")
        
        return self.test_routine_id is not None
    
    def test_client_login_and_access(self):
        """Test 6: Client Login and Restricted Access"""
        print("=== Testing Client Login and Access ===")
        
        if not self.test_client_id:
            self.log_result("Client Login", False, "No test client available")
            return False
        
        # Test Client Login
        try:
            response = requests.post(
                f"{self.base_url}/auth/client/login",
                params={"client_id": self.test_client_id},
                timeout=10
            )
            if response.status_code == 200:
                auth_data = response.json()
                if "access_token" in auth_data and "user" in auth_data:
                    self.client_token = auth_data["access_token"]
                    self.log_result("Client Login", True, f"Client authenticated: {auth_data['user']['name']}")
                else:
                    self.log_result("Client Login", False, "Invalid client login response format", response)
                    return False
            else:
                self.log_result("Client Login", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Client Login", False, f"Connection error: {str(e)}")
            return False
        
        # Test Invalid Client ID
        try:
            response = requests.post(
                f"{self.base_url}/auth/client/login",
                params={"client_id": "invalid-client-id"},
                timeout=10
            )
            if response.status_code == 401:
                self.log_result("Invalid Client ID", True, "Correctly rejected invalid client ID")
            else:
                self.log_result("Invalid Client ID", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Client ID", False, f"Connection error: {str(e)}")
        
        return self.client_token is not None
    
    def test_client_workout_logging(self):
        """Test 7: Client Workout Logging with Restrictions"""
        print("=== Testing Client Workout Logging ===")
        
        if not self.client_token:
            self.log_result("Client Workout Logging", False, "No client token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Test Get Client Routine
        try:
            response = requests.get(f"{self.base_url}/client/routine", headers=headers, timeout=10)
            if response.status_code == 200:
                routine_data = response.json()
                if "routine" in routine_data:
                    routine = routine_data["routine"]
                    if routine:
                        # Check if exercises have tips
                        has_tips = any(ex.get("tips") for ex in routine.get("exercises", []))
                        if has_tips:
                            self.log_result("Get Client Routine with Tips", True, f"Retrieved assigned routine: {routine['name']} with exercise tips")
                        else:
                            self.log_result("Get Client Routine with Tips", True, f"Retrieved assigned routine: {routine['name']}")
                    else:
                        self.log_result("Get Client Routine with Tips", True, "No routine assigned (expected for new client)")
                else:
                    self.log_result("Get Client Routine with Tips", False, "Invalid routine response format", response)
            else:
                self.log_result("Get Client Routine with Tips", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Client Routine with Tips", False, f"Connection error: {str(e)}")
        
        # Test Log Workout
        try:
            workout_data = {
                "routine_id": self.test_routine_id if self.test_routine_id else "test-routine",
                "routine_name": "Upper Body Strength",
                "exercises": [
                    {
                        "exercise_id": self.test_exercise_ids[0] if self.test_exercise_ids else "test-exercise",
                        "exercise_name": "Bench Press",
                        "sets": [
                            {"set_number": 1, "weight_kg": 80.0, "reps": 8, "rir": 2},
                            {"set_number": 2, "weight_kg": 82.5, "reps": 6, "rir": 1},
                            {"set_number": 3, "weight_kg": 85.0, "reps": 5, "rir": 0}
                        ]
                    }
                ],
                "notes": "Felt strong today, good form throughout",
                "duration_minutes": 45
            }
            response = requests.post(
                f"{self.base_url}/client/workouts",
                json=workout_data,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                workout = response.json()
                if "id" in workout and workout["client_id"] == self.test_client_id:
                    self.log_result("Log Client Workout", True, f"Logged workout with {len(workout['exercises'])} exercises")
                else:
                    self.log_result("Log Client Workout", False, "Invalid workout logging response", response)
            else:
                self.log_result("Log Client Workout", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Log Client Workout", False, f"Connection error: {str(e)}")
        
        # Test Get Client Workout History
        try:
            response = requests.get(f"{self.base_url}/client/workouts", headers=headers, timeout=10)
            if response.status_code == 200:
                workouts = response.json()
                if isinstance(workouts, list):
                    self.log_result("Get Client Workouts", True, f"Retrieved {len(workouts)} workout(s) from history")
                else:
                    self.log_result("Get Client Workouts", False, "Invalid workouts response format", response)
            else:
                self.log_result("Get Client Workouts", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Client Workouts", False, f"Connection error: {str(e)}")
        
        return True
    
    def test_body_measurements_tracking(self):
        """Test 8: Body Measurements and Progress Tracking"""
        print("=== Testing Body Measurements and Progress Tracking ===")
        
        if not self.coach_token or not self.test_client_id:
            self.log_result("Body Measurements", False, "Missing coach token or client ID")
            return False
        
        headers = {"Authorization": f"Bearer {self.coach_token}"}
        
        # Test Add Client Measurements
        try:
            measurement_data = {
                "weight_kg": 75.5,
                "body_fat_percentage": 15.2,
                "measurements": {
                    "chest": 102.0,
                    "waist": 85.0,
                    "arms": 38.5,
                    "thighs": 58.0,
                    "shoulders": 118.0
                }
            }
            response = requests.post(
                f"{self.base_url}/coach/measurements/{self.test_client_id}",
                json=measurement_data,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                measurement = response.json()
                if "id" in measurement and measurement["client_id"] == self.test_client_id:
                    self.log_result("Add Client Measurements", True, f"Added measurements: {measurement['weight_kg']}kg, {measurement['body_fat_percentage']}% BF")
                else:
                    self.log_result("Add Client Measurements", False, "Invalid measurement response", response)
            else:
                self.log_result("Add Client Measurements", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Add Client Measurements", False, f"Connection error: {str(e)}")
        
        # Test Get Client Measurements
        try:
            response = requests.get(
                f"{self.base_url}/coach/measurements/{self.test_client_id}",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                measurements = response.json()
                if isinstance(measurements, list):
                    self.log_result("Get Client Measurements", True, f"Retrieved {len(measurements)} measurement record(s)")
                else:
                    self.log_result("Get Client Measurements", False, "Invalid measurements response format", response)
            else:
                self.log_result("Get Client Measurements", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Client Measurements", False, f"Connection error: {str(e)}")
        
        return True
    
    def test_progress_comparison_dashboard(self):
        """Test 9: Progress Comparison Dashboard"""
        print("=== Testing Progress Comparison Dashboard ===")
        
        if not self.coach_token:
            self.log_result("Progress Comparison", False, "No coach token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.coach_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/coach/progress-comparison", headers=headers, timeout=10)
            if response.status_code == 200:
                comparison_data = response.json()
                if isinstance(comparison_data, list):
                    if len(comparison_data) > 0:
                        # Verify data structure
                        first_client = comparison_data[0]
                        required_fields = ["client", "latest_measurement", "workouts_this_month", "total_volume_this_month"]
                        if all(field in first_client for field in required_fields):
                            self.log_result("Progress Comparison Dashboard", True, f"Retrieved comparison data for {len(comparison_data)} client(s)")
                        else:
                            self.log_result("Progress Comparison Dashboard", False, "Comparison data missing required fields", response)
                    else:
                        self.log_result("Progress Comparison Dashboard", True, "No clients for comparison (empty data)")
                else:
                    self.log_result("Progress Comparison Dashboard", False, "Invalid comparison response format", response)
            else:
                self.log_result("Progress Comparison Dashboard", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Progress Comparison Dashboard", False, f"Connection error: {str(e)}")
        
        return True
    
    def test_security_access_control(self):
        """Test 10: Security and Access Control"""
        print("=== Testing Security and Access Control ===")
        
        # Test Coach endpoints reject client tokens
        if self.client_token:
            client_headers = {"Authorization": f"Bearer {self.client_token}"}
            try:
                response = requests.get(f"{self.base_url}/coach/dashboard", headers=client_headers, timeout=10)
                if response.status_code == 403:
                    self.log_result("Coach Endpoint Security", True, "Client token correctly rejected from coach endpoint")
                else:
                    self.log_result("Coach Endpoint Security", False, f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Coach Endpoint Security", False, f"Connection error: {str(e)}")
        
        # Test Client endpoints reject coach tokens
        if self.coach_token:
            coach_headers = {"Authorization": f"Bearer {self.coach_token}"}
            try:
                response = requests.get(f"{self.base_url}/client/routine", headers=coach_headers, timeout=10)
                if response.status_code == 403:
                    self.log_result("Client Endpoint Security", True, "Coach token correctly rejected from client endpoint")
                else:
                    self.log_result("Client Endpoint Security", False, f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_result("Client Endpoint Security", False, f"Connection error: {str(e)}")
        
        # Test endpoints without tokens
        try:
            response = requests.get(f"{self.base_url}/coach/dashboard", timeout=10)
            if response.status_code == 401:
                self.log_result("No Token Security", True, "Correctly rejected request without token")
            else:
                self.log_result("No Token Security", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("No Token Security", False, f"Connection error: {str(e)}")
        
        return True
    
    def run_all_tests(self):
        """Run all backend tests in priority order"""
        print("🏋️ Starting Comprehensive Backend Testing for Coach-Client Management System")
        print(f"Backend URL: {self.base_url}")
        print("=" * 70)
        
        # Test in priority order as specified
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication System", self.test_authentication_system),
            ("Coach Dashboard & Client Management", self.test_coach_dashboard_client_management),
            ("Exercise Tips Management", self.test_exercise_tips_management),
            ("Routine Creation & Assignment", self.test_routine_creation_assignment),
            ("Client Login & Access", self.test_client_login_and_access),
            ("Client Workout Logging", self.test_client_workout_logging),
            ("Body Measurements & Tracking", self.test_body_measurements_tracking),
            ("Progress Comparison Dashboard", self.test_progress_comparison_dashboard),
            ("Security & Access Control", self.test_security_access_control)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_result(f"{test_name} (Exception)", False, f"Unexpected error: {str(e)}")
        
        # Print final results
        print("=" * 70)
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
    tester = CoachClientSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)