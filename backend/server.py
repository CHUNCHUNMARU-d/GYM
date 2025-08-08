import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional
import uuid

# Database setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'workout_tracker')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
exercises_collection = db.exercises
workouts_collection = db.workouts
users_collection = db.users

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Exercise(BaseModel):
    id: str
    name: str
    muscle_group: str
    created_at: datetime

class WorkoutSet(BaseModel):
    set_number: int
    weight_kg: float
    reps: int
    rir: int  # Reps in Reserve

class WorkoutExercise(BaseModel):
    exercise_id: str
    exercise_name: str
    sets: List[WorkoutSet]

class Workout(BaseModel):
    id: str
    user_id: str
    date: datetime
    exercises: List[WorkoutExercise]
    notes: Optional[str] = ""
    duration_minutes: Optional[int] = 0

class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = ""
    created_at: datetime

# API Routes

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Workout Tracker API is running"}

# User endpoints
@app.post("/api/users")
async def create_user(name: str, email: str = ""):
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "name": name,
        "email": email,
        "created_at": datetime.now(timezone.utc)
    }
    users_collection.insert_one(user)
    user.pop("_id", None)  # Remove MongoDB ObjectId before returning
    return user

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    user = users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.pop("_id", None)
    return user

# Exercise endpoints
@app.get("/api/exercises")
async def get_exercises():
    exercises = list(exercises_collection.find({}, {"_id": 0}))
    return exercises

@app.post("/api/exercises")
async def create_exercise(name: str, muscle_group: str):
    # Check if exercise already exists
    existing = exercises_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if existing:
        raise HTTPException(status_code=400, detail="Exercise already exists")
    
    exercise_id = str(uuid.uuid4())
    exercise = {
        "id": exercise_id,
        "name": name,
        "muscle_group": muscle_group,
        "created_at": datetime.now(timezone.utc)
    }
    exercises_collection.insert_one(exercise)
    exercise.pop("_id", None)
    return exercise

@app.get("/api/exercises/search")
async def search_exercises(query: str):
    exercises = list(exercises_collection.find(
        {"name": {"$regex": query, "$options": "i"}}, 
        {"_id": 0}
    ))
    return exercises

# Workout endpoints
@app.post("/api/workouts")
async def create_workout(workout_data: dict):
    workout_id = str(uuid.uuid4())
    workout = {
        "id": workout_id,
        "user_id": workout_data.get("user_id", "default_user"),
        "date": datetime.now(timezone.utc),
        "exercises": workout_data.get("exercises", []),
        "notes": workout_data.get("notes", ""),
        "duration_minutes": workout_data.get("duration_minutes", 0)
    }
    workouts_collection.insert_one(workout)
    workout.pop("_id", None)
    return workout

@app.get("/api/workouts/{user_id}")
async def get_user_workouts(user_id: str, limit: int = 10):
    workouts = list(workouts_collection.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("date", -1).limit(limit))
    return workouts

@app.get("/api/workouts/{user_id}/stats")
async def get_workout_stats(user_id: str, exercise_id: str = None):
    """Get workout statistics for a user, optionally filtered by exercise"""
    query = {"user_id": user_id}
    workouts = list(workouts_collection.find(query, {"_id": 0}))
    
    if not workouts:
        return {"total_workouts": 0, "exercise_stats": {}}
    
    # Calculate stats
    exercise_stats = {}
    total_workouts = len(workouts)
    
    for workout in workouts:
        for exercise in workout.get("exercises", []):
            ex_id = exercise["exercise_id"]
            ex_name = exercise["exercise_name"]
            
            if exercise_id and ex_id != exercise_id:
                continue
                
            if ex_id not in exercise_stats:
                exercise_stats[ex_id] = {
                    "name": ex_name,
                    "total_sets": 0,
                    "total_reps": 0,
                    "total_volume_kg": 0,
                    "max_weight_kg": 0,
                    "avg_weight_kg": 0,
                    "avg_reps": 0,
                    "avg_rir": 0,
                    "sessions": 0
                }
            
            stats = exercise_stats[ex_id]
            stats["sessions"] += 1
            
            for set_data in exercise["sets"]:
                stats["total_sets"] += 1
                stats["total_reps"] += set_data["reps"]
                volume = set_data["weight_kg"] * set_data["reps"]
                stats["total_volume_kg"] += volume
                stats["max_weight_kg"] = max(stats["max_weight_kg"], set_data["weight_kg"])
    
    # Calculate averages
    for ex_id, stats in exercise_stats.items():
        if stats["total_sets"] > 0:
            stats["avg_weight_kg"] = round(stats["total_volume_kg"] / stats["total_reps"], 2)
            stats["avg_reps"] = round(stats["total_reps"] / stats["total_sets"], 1)
    
    return {
        "total_workouts": total_workouts,
        "exercise_stats": exercise_stats
    }

@app.delete("/api/workouts/{workout_id}")
async def delete_workout(workout_id: str):
    result = workouts_collection.delete_one({"id": workout_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": "Workout deleted successfully"}

# Initialize with some default exercises
@app.on_event("startup")
async def startup_event():
    # Check if exercises collection is empty
    if exercises_collection.count_documents({}) == 0:
        default_exercises = [
            {"id": str(uuid.uuid4()), "name": "Bench Press", "muscle_group": "Chest", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Squat", "muscle_group": "Legs", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Deadlift", "muscle_group": "Back", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Overhead Press", "muscle_group": "Shoulders", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Barbell Row", "muscle_group": "Back", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Pull-ups", "muscle_group": "Back", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Dips", "muscle_group": "Chest", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Bicep Curls", "muscle_group": "Arms", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Tricep Extensions", "muscle_group": "Arms", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Leg Press", "muscle_group": "Legs", "created_at": datetime.now(timezone.utc)}
        ]
        exercises_collection.insert_many(default_exercises)
        print("Default exercises added to database")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)