import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [currentView, setCurrentView] = useState('workouts');
  const [exercises, setExercises] = useState([]);
  const [workouts, setWorkouts] = useState([]);
  const [currentWorkout, setCurrentWorkout] = useState([]);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [workoutStats, setWorkoutStats] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [user] = useState({ id: 'default_user', name: 'Workout User' });

  // Load exercises and workouts on component mount
  useEffect(() => {
    loadExercises();
    loadWorkouts();
    loadStats();
  }, []);

  const loadExercises = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/exercises`);
      setExercises(response.data);
    } catch (error) {
      console.error('Error loading exercises:', error);
    }
  };

  const loadWorkouts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/workouts/${user.id}`);
      setWorkouts(response.data);
    } catch (error) {
      console.error('Error loading workouts:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/workouts/${user.id}/stats`);
      setWorkoutStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const saveWorkout = async () => {
    if (currentWorkout.length === 0) {
      alert('Please add at least one exercise to save the workout');
      return;
    }

    setIsLoading(true);
    try {
      const workoutData = {
        user_id: user.id,
        exercises: currentWorkout
      };
      
      await axios.post(`${API_BASE_URL}/api/workouts`, workoutData);
      setCurrentWorkout([]);
      loadWorkouts();
      loadStats();
      alert('Workout saved successfully!');
    } catch (error) {
      console.error('Error saving workout:', error);
      alert('Error saving workout. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const addExerciseToWorkout = (exercise) => {
    const existingIndex = currentWorkout.findIndex(w => w.exercise_id === exercise.id);
    
    if (existingIndex >= 0) {
      // Exercise already in workout, just select it
      setSelectedExercise(currentWorkout[existingIndex]);
    } else {
      // Add new exercise to workout
      const newWorkoutExercise = {
        exercise_id: exercise.id,
        exercise_name: exercise.name,
        sets: []
      };
      setCurrentWorkout([...currentWorkout, newWorkoutExercise]);
      setSelectedExercise(newWorkoutExercise);
    }
  };

  const updateExerciseSets = (exerciseId, sets) => {
    setCurrentWorkout(prev => 
      prev.map(exercise => 
        exercise.exercise_id === exerciseId 
          ? { ...exercise, sets }
          : exercise
      )
    );
  };

  const removeExerciseFromWorkout = (exerciseId) => {
    setCurrentWorkout(prev => prev.filter(exercise => exercise.exercise_id !== exerciseId));
    if (selectedExercise && selectedExercise.exercise_id === exerciseId) {
      setSelectedExercise(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">💪 Workout Tracker</h1>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentView('workouts')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentView === 'workouts'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Current
              </button>
              <button
                onClick={() => setCurrentView('history')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentView === 'history'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                History
              </button>
              <button
                onClick={() => setCurrentView('stats')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentView === 'stats'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Stats
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Current Workout View */}
        {currentView === 'workouts' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Exercise Selection */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Exercise</h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {exercises.map(exercise => (
                  <button
                    key={exercise.id}
                    onClick={() => addExerciseToWorkout(exercise)}
                    className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
                  >
                    <div className="font-medium text-gray-900">{exercise.name}</div>
                    <div className="text-sm text-gray-500">{exercise.muscle_group}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Current Workout */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Current Workout</h2>
                {currentWorkout.length > 0 && (
                  <button
                    onClick={saveWorkout}
                    disabled={isLoading}
                    className="btn-primary"
                  >
                    {isLoading ? 'Saving...' : 'Save Workout'}
                  </button>
                )}
              </div>
              
              {currentWorkout.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Select exercises to start your workout</p>
              ) : (
                <div className="space-y-3">
                  {currentWorkout.map(exercise => (
                    <div
                      key={exercise.exercise_id}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        selectedExercise && selectedExercise.exercise_id === exercise.exercise_id
                          ? 'border-blue-300 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedExercise(exercise)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">{exercise.exercise_name}</div>
                          <div className="text-sm text-gray-500">{exercise.sets.length} sets</div>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            removeExerciseFromWorkout(exercise.exercise_id);
                          }}
                          className="text-red-500 hover:text-red-700 p-1"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Set Details */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Set Details</h2>
              
              {selectedExercise ? (
                <SetInputForm
                  exercise={selectedExercise}
                  onUpdateSets={(sets) => updateExerciseSets(selectedExercise.exercise_id, sets)}
                />
              ) : (
                <p className="text-gray-500 text-center py-8">Select an exercise to log sets</p>
              )}
            </div>
          </div>
        )}

        {/* History View */}
        {currentView === 'history' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Workout History</h2>
            
            {workouts.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No workouts recorded yet</p>
            ) : (
              <div className="space-y-4">
                {workouts.map(workout => (
                  <div key={workout.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="text-lg font-medium text-gray-900">
                        {new Date(workout.date).toLocaleDateString()}
                      </div>
                      <div className="text-sm text-gray-500">
                        {workout.exercises.length} exercises
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      {workout.exercises.map((exercise, idx) => (
                        <div key={idx} className="bg-gray-50 rounded p-3">
                          <div className="font-medium text-gray-900 mb-2">{exercise.exercise_name}</div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                            {exercise.sets.map((set, setIdx) => (
                              <div key={setIdx} className="text-sm bg-white rounded p-2">
                                <span className="font-medium">Set {set.set_number}:</span> {set.weight_kg}kg × {set.reps} (RIR: {set.rir})
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Stats View */}
        {currentView === 'stats' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Workout Statistics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">{workoutStats.total_workouts || 0}</div>
                <div className="text-sm text-gray-600">Total Workouts</div>
              </div>
              
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">
                  {Object.keys(workoutStats.exercise_stats || {}).length}
                </div>
                <div className="text-sm text-gray-600">Exercises Tracked</div>
              </div>
              
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-600">
                  {Object.values(workoutStats.exercise_stats || {}).reduce((sum, stat) => sum + stat.total_sets, 0)}
                </div>
                <div className="text-sm text-gray-600">Total Sets</div>
              </div>
            </div>

            {/* Exercise Stats */}
            {workoutStats.exercise_stats && Object.keys(workoutStats.exercise_stats).length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Exercise Progress</h3>
                <div className="space-y-4">
                  {Object.values(workoutStats.exercise_stats).map(stat => (
                    <div key={stat.name} className="border border-gray-200 rounded-lg p-4">
                      <div className="font-medium text-gray-900 mb-2">{stat.name}</div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <div className="text-gray-500">Max Weight</div>
                          <div className="font-medium">{stat.max_weight_kg}kg</div>
                        </div>
                        <div>
                          <div className="text-gray-500">Avg Weight</div>
                          <div className="font-medium">{stat.avg_weight_kg}kg</div>
                        </div>
                        <div>
                          <div className="text-gray-500">Total Volume</div>
                          <div className="font-medium">{Math.round(stat.total_volume_kg)}kg</div>
                        </div>
                        <div>
                          <div className="text-gray-500">Sessions</div>
                          <div className="font-medium">{stat.sessions}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Set Input Component
function SetInputForm({ exercise, onUpdateSets }) {
  const [sets, setSets] = useState(exercise.sets);

  useEffect(() => {
    setSets(exercise.sets);
  }, [exercise]);

  const addSet = () => {
    if (sets.length >= 5) {
      alert('Maximum 5 sets allowed per exercise');
      return;
    }
    
    const newSet = {
      set_number: sets.length + 1,
      weight_kg: sets.length > 0 ? sets[sets.length - 1].weight_kg : 0,
      reps: sets.length > 0 ? sets[sets.length - 1].reps : 8,
      rir: sets.length > 0 ? sets[sets.length - 1].rir : 2
    };
    
    const newSets = [...sets, newSet];
    setSets(newSets);
    onUpdateSets(newSets);
  };

  const updateSet = (index, field, value) => {
    const newSets = sets.map((set, i) => 
      i === index ? { ...set, [field]: parseFloat(value) || 0 } : set
    );
    setSets(newSets);
    onUpdateSets(newSets);
  };

  const removeSet = (index) => {
    const newSets = sets.filter((_, i) => i !== index)
      .map((set, i) => ({ ...set, set_number: i + 1 }));
    setSets(newSets);
    onUpdateSets(newSets);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">{exercise.exercise_name}</h3>
        <button
          onClick={addSet}
          disabled={sets.length >= 5}
          className="btn-secondary text-sm"
        >
          Add Set
        </button>
      </div>

      <div className="space-y-3">
        {sets.map((set, index) => (
          <div key={index} className="grid grid-cols-4 gap-2 items-center p-3 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-700">Set {set.set_number}</div>
            
            <div>
              <label className="block text-xs text-gray-500 mb-1">Weight (kg)</label>
              <input
                type="number"
                step="0.5"
                value={set.weight_kg}
                onChange={(e) => updateSet(index, 'weight_kg', e.target.value)}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-xs text-gray-500 mb-1">Reps</label>
              <input
                type="number"
                value={set.reps}
                onChange={(e) => updateSet(index, 'reps', e.target.value)}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <div className="flex-1">
                <label className="block text-xs text-gray-500 mb-1">RIR</label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={set.rir}
                  onChange={(e) => updateSet(index, 'rir', e.target.value)}
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button
                onClick={() => removeSet(index)}
                className="text-red-500 hover:text-red-700 p-1 mt-4"
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>

      {sets.length === 0 && (
        <p className="text-gray-500 text-center py-4">Click "Add Set" to start logging</p>
      )}
    </div>
  );
}

export default App;