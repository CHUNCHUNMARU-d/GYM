import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
import uuid
import hashlib
import jwt
from passlib.context import CryptContext

# Database setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'coach_client_system')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
coaches_collection = db.coaches
clients_collection = db.clients
exercises_collection = db.exercises
routines_collection = db.routines
workouts_collection = db.workouts
measurements_collection = db.measurements

app = FastAPI()

# Security setup
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Coach(BaseModel):
    id: str
    username: str
    password_hash: str
    name: str
    email: str
    created_at: datetime

class Client(BaseModel):
    id: str
    name: str
    email: Optional[str] = ""
    coach_id: str
    created_at: datetime
    is_active: bool = True

class Exercise(BaseModel):
    id: str
    name: str
    muscle_group: str
    tips: str
    created_at: datetime

class RoutineExercise(BaseModel):
    exercise_id: str
    exercise_name: str
    target_sets: int
    target_reps: str  # e.g., "8-12"
    target_weight: Optional[float] = None
    rest_seconds: Optional[int] = 90

class Routine(BaseModel):
    id: str
    name: str
    coach_id: str
    exercises: List[RoutineExercise]
    assigned_clients: List[str]
    created_at: datetime
    is_active: bool = True

class WorkoutSet(BaseModel):
    set_number: int
    weight_kg: float
    reps: int
    rir: int

class WorkoutExercise(BaseModel):
    exercise_id: str
    exercise_name: str
    sets: List[WorkoutSet]

class Workout(BaseModel):
    id: str
    client_id: str
    routine_id: str
    routine_name: str
    date: datetime
    exercises: List[WorkoutExercise]
    notes: Optional[str] = ""
    duration_minutes: Optional[int] = 0

class BodyMeasurement(BaseModel):
    id: str
    client_id: str
    date: datetime
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    measurements: Dict[str, float]  # chest, waist, arms, thighs, etc.

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("type")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "user_type": user_type}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_coach(token_data: dict = Depends(verify_token)):
    if token_data["user_type"] != "coach":
        raise HTTPException(status_code=403, detail="Coach access required")
    coach = coaches_collection.find_one({"id": token_data["user_id"]})
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    coach.pop("_id", None)
    return coach

def get_current_client(token_data: dict = Depends(verify_token)):
    if token_data["user_type"] != "client":
        raise HTTPException(status_code=403, detail="Client access required")
    client = clients_collection.find_one({"id": token_data["user_id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.pop("_id", None)
    return client

# API Routes

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Coach-Client System API is running"}

# Authentication endpoints
@app.post("/api/auth/coach/login")
async def coach_login(username: str, password: str):
    coach = coaches_collection.find_one({"username": username})
    if not coach or not verify_password(password, coach["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": coach["id"], "type": "coach"})
    coach.pop("_id", None)
    coach.pop("password_hash", None)
    return {"access_token": access_token, "token_type": "bearer", "user": coach}

@app.post("/api/auth/client/login")
async def client_login(client_id: str):
    client = clients_collection.find_one({"id": client_id, "is_active": True})
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client ID")
    
    access_token = create_access_token({"sub": client["id"], "type": "client"})
    client.pop("_id", None)
    return {"access_token": access_token, "token_type": "bearer", "user": client}

# Coach endpoints
@app.get("/api/coach/dashboard")
async def get_coach_dashboard(coach: dict = Depends(get_current_coach)):
    # Get all clients
    clients = list(clients_collection.find({"coach_id": coach["id"], "is_active": True}, {"_id": 0}))
    
    # Get total workouts this week
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    total_workouts = workouts_collection.count_documents({
        "date": {"$gte": week_ago}
    })
    
    # Get active routines
    active_routines = routines_collection.count_documents({
        "coach_id": coach["id"], 
        "is_active": True
    })
    
    return {
        "coach": coach,
        "total_clients": len(clients),
        "total_workouts_this_week": total_workouts,
        "active_routines": active_routines,
        "clients": clients
    }

@app.get("/api/coach/clients")
async def get_coach_clients(coach: dict = Depends(get_current_coach)):
    clients = list(clients_collection.find({"coach_id": coach["id"]}, {"_id": 0}))
    return clients

@app.post("/api/coach/clients")
async def create_client(name: str, email: str = "", coach: dict = Depends(get_current_coach)):
    client_id = str(uuid.uuid4())
    client = {
        "id": client_id,
        "name": name,
        "email": email,
        "coach_id": coach["id"],
        "created_at": datetime.now(timezone.utc),
        "is_active": True
    }
    clients_collection.insert_one(client)
    client.pop("_id", None)
    return client

@app.get("/api/coach/client/{client_id}/progress")
async def get_client_progress(client_id: str, coach: dict = Depends(get_current_coach)):
    # Verify client belongs to coach
    client = clients_collection.find_one({"id": client_id, "coach_id": coach["id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get workouts
    workouts = list(workouts_collection.find(
        {"client_id": client_id},
        {"_id": 0}
    ).sort("date", -1).limit(20))
    
    # Get measurements
    measurements = list(measurements_collection.find(
        {"client_id": client_id},
        {"_id": 0}
    ).sort("date", -1).limit(10))
    
    # Calculate exercise stats
    exercise_stats = {}
    for workout in workouts:
        for exercise in workout.get("exercises", []):
            ex_id = exercise["exercise_id"]
            ex_name = exercise["exercise_name"]
            
            if ex_id not in exercise_stats:
                exercise_stats[ex_id] = {
                    "name": ex_name,
                    "total_sets": 0,
                    "max_weight_kg": 0,
                    "avg_weight_kg": 0,
                    "total_volume_kg": 0,
                    "total_reps": 0,
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
        if stats["total_reps"] > 0:
            stats["avg_weight_kg"] = round(stats["total_volume_kg"] / stats["total_reps"], 2)
    
    client.pop("_id", None)
    return {
        "client": client,
        "workouts": workouts,
        "measurements": measurements,
        "exercise_stats": exercise_stats
    }

# Exercise management
@app.get("/api/exercises")
async def get_exercises():
    exercises = list(exercises_collection.find({}, {"_id": 0}))
    return exercises

@app.post("/api/coach/exercises")
async def create_exercise(name: str, muscle_group: str, tips: str = "", coach: dict = Depends(get_current_coach)):
    existing = exercises_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if existing:
        raise HTTPException(status_code=400, detail="Exercise already exists")
    
    exercise_id = str(uuid.uuid4())
    exercise = {
        "id": exercise_id,
        "name": name,
        "muscle_group": muscle_group,
        "tips": tips,
        "created_at": datetime.now(timezone.utc)
    }
    exercises_collection.insert_one(exercise)
    exercise.pop("_id", None)
    return exercise

@app.put("/api/coach/exercises/{exercise_id}")
async def update_exercise_tips(exercise_id: str, tips: str, coach: dict = Depends(get_current_coach)):
    result = exercises_collection.update_one(
        {"id": exercise_id},
        {"$set": {"tips": tips}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    exercise = exercises_collection.find_one({"id": exercise_id}, {"_id": 0})
    return exercise

# Routine management
@app.get("/api/coach/routines")
async def get_coach_routines(coach: dict = Depends(get_current_coach)):
    routines = list(routines_collection.find({"coach_id": coach["id"]}, {"_id": 0}))
    return routines

@app.post("/api/coach/routines")
async def create_routine(routine_data: dict, coach: dict = Depends(get_current_coach)):
    routine_id = str(uuid.uuid4())
    routine = {
        "id": routine_id,
        "name": routine_data["name"],
        "coach_id": coach["id"],
        "exercises": routine_data.get("exercises", []),
        "assigned_clients": routine_data.get("assigned_clients", []),
        "created_at": datetime.now(timezone.utc),
        "is_active": True
    }
    routines_collection.insert_one(routine)
    routine.pop("_id", None)
    return routine

@app.put("/api/coach/routines/{routine_id}")
async def update_routine(routine_id: str, routine_data: dict, coach: dict = Depends(get_current_coach)):
    result = routines_collection.update_one(
        {"id": routine_id, "coach_id": coach["id"]},
        {"$set": {
            "name": routine_data.get("name"),
            "exercises": routine_data.get("exercises", []),
            "assigned_clients": routine_data.get("assigned_clients", [])
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    routine = routines_collection.find_one({"id": routine_id}, {"_id": 0})
    return routine

# Client endpoints
@app.get("/api/client/routine")
async def get_client_routine(client: dict = Depends(get_current_client)):
    routine = routines_collection.find_one({
        "assigned_clients": client["id"],
        "is_active": True
    }, {"_id": 0})
    
    if not routine:
        return {"routine": None, "message": "No routine assigned"}
    
    # Get exercise details with tips
    for exercise in routine["exercises"]:
        exercise_detail = exercises_collection.find_one({"id": exercise["exercise_id"]}, {"_id": 0})
        if exercise_detail:
            exercise["tips"] = exercise_detail.get("tips", "")
    
    return {"routine": routine}

@app.post("/api/client/workouts")
async def log_client_workout(workout_data: dict, client: dict = Depends(get_current_client)):
    workout_id = str(uuid.uuid4())
    workout = {
        "id": workout_id,
        "client_id": client["id"],
        "routine_id": workout_data.get("routine_id"),
        "routine_name": workout_data.get("routine_name", ""),
        "date": datetime.now(timezone.utc),
        "exercises": workout_data.get("exercises", []),
        "notes": workout_data.get("notes", ""),
        "duration_minutes": workout_data.get("duration_minutes", 0)
    }
    workouts_collection.insert_one(workout)
    workout.pop("_id", None)
    return workout

@app.get("/api/client/workouts")
async def get_client_workouts(client: dict = Depends(get_current_client), limit: int = 10):
    workouts = list(workouts_collection.find(
        {"client_id": client["id"]},
        {"_id": 0}
    ).sort("date", -1).limit(limit))
    return workouts

# Body measurements
@app.post("/api/coach/measurements/{client_id}")
async def add_client_measurements(
    client_id: str, 
    measurement_data: dict, 
    coach: dict = Depends(get_current_coach)
):
    # Verify client belongs to coach
    client = clients_collection.find_one({"id": client_id, "coach_id": coach["id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    measurement_id = str(uuid.uuid4())
    measurement = {
        "id": measurement_id,
        "client_id": client_id,
        "date": datetime.now(timezone.utc),
        "weight_kg": measurement_data.get("weight_kg"),
        "body_fat_percentage": measurement_data.get("body_fat_percentage"),
        "measurements": measurement_data.get("measurements", {})
    }
    measurements_collection.insert_one(measurement)
    measurement.pop("_id", None)
    return measurement

@app.get("/api/coach/measurements/{client_id}")
async def get_client_measurements(client_id: str, coach: dict = Depends(get_current_coach)):
    # Verify client belongs to coach
    client = clients_collection.find_one({"id": client_id, "coach_id": coach["id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    measurements = list(measurements_collection.find(
        {"client_id": client_id},
        {"_id": 0}
    ).sort("date", -1))
    return measurements

# Progress comparison
@app.get("/api/coach/progress-comparison")
async def get_progress_comparison(coach: dict = Depends(get_current_coach)):
    clients = list(clients_collection.find({"coach_id": coach["id"], "is_active": True}, {"_id": 0}))
    
    comparison_data = []
    for client in clients:
        # Get latest measurements
        latest_measurement = measurements_collection.find_one(
            {"client_id": client["id"]},
            {"_id": 0},
            sort=[("date", -1)]
        )
        
        # Get workout count this month
        month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        workout_count = workouts_collection.count_documents({
            "client_id": client["id"],
            "date": {"$gte": month_ago}
        })
        
        # Get total volume this month
        workouts = list(workouts_collection.find({
            "client_id": client["id"],
            "date": {"$gte": month_ago}
        }))
        
        total_volume = 0
        for workout in workouts:
            for exercise in workout.get("exercises", []):
                for set_data in exercise.get("sets", []):
                    total_volume += set_data["weight_kg"] * set_data["reps"]
        
        comparison_data.append({
            "client": client,
            "latest_measurement": latest_measurement,
            "workouts_this_month": workout_count,
            "total_volume_this_month": round(total_volume, 2)
        })
    
    return comparison_data

# Initialize default data
@app.on_event("startup")
async def startup_event():
    # Create default coach if not exists
    coach = coaches_collection.find_one({"username": "coach"})
    if not coach:
        coach_id = str(uuid.uuid4())
        default_coach = {
            "id": coach_id,
            "username": "coach",
            "password_hash": get_password_hash("coach123"),  # Change this!
            "name": "Default Coach",
            "email": "coach@gym.com",
            "created_at": datetime.now(timezone.utc)
        }
        coaches_collection.insert_one(default_coach)
        print("Default coach created - Username: coach, Password: coach123")
    
    # Create default exercises if not exist
    if exercises_collection.count_documents({}) == 0:
        default_exercises = [
            {"id": str(uuid.uuid4()), "name": "Bench Press", "muscle_group": "Chest", "tips": "Keep your feet flat on the floor, squeeze shoulder blades together, and maintain a slight arch in your back.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Squat", "muscle_group": "Legs", "tips": "Keep your chest up, knees tracking over toes, and descend until hips are below knee level.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Deadlift", "muscle_group": "Back", "tips": "Keep the bar close to your body, maintain neutral spine, and drive through your heels.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Overhead Press", "muscle_group": "Shoulders", "tips": "Engage your core, keep elbows slightly forward, and press straight up over your head.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Barbell Row", "muscle_group": "Back", "tips": "Hinge at the hips, keep chest up, and pull the bar to your lower chest/upper abdomen.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Pull-ups", "muscle_group": "Back", "tips": "Start with arms fully extended, pull your chest to the bar, and control the descent.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Dips", "muscle_group": "Chest", "tips": "Keep your body upright, lower until shoulders are below elbows, and push up smoothly.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Bicep Curls", "muscle_group": "Arms", "tips": "Keep elbows stationary, squeeze biceps at the top, and control the negative.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Tricep Extensions", "muscle_group": "Arms", "tips": "Keep elbows fixed, lower weight behind your head, and extend fully.", "created_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "name": "Leg Press", "muscle_group": "Legs", "tips": "Place feet shoulder-width apart, lower until knees reach 90 degrees, and push through heels.", "created_at": datetime.now(timezone.utc)}
        ]
        exercises_collection.insert_many(default_exercises)
        print("Default exercises with tips added to database")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)