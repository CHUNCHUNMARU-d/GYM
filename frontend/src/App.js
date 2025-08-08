import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [userType, setUserType] = useState(null); // 'coach' or 'client'
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [currentView, setCurrentView] = useState('dashboard');

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const savedUserType = localStorage.getItem('userType');
    
    if (token && savedUser && savedUserType) {
      setUser(JSON.parse(savedUser));
      setUserType(savedUserType);
    }
  }, [token]);

  const handleLogin = (userData, userType, authToken) => {
    setUser(userData);
    setUserType(userType);
    setToken(authToken);
    localStorage.setItem('token', authToken);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('userType', userType);
  };

  const handleLogout = () => {
    setUser(null);
    setUserType(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('userType');
    setCurrentView('dashboard');
  };

  if (!user || !token) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  if (userType === 'coach') {
    return (
      <CoachDashboard 
        user={user} 
        token={token} 
        currentView={currentView}
        setCurrentView={setCurrentView}
        onLogout={handleLogout}
      />
    );
  } else {
    return (
      <ClientInterface 
        user={user} 
        token={token} 
        onLogout={handleLogout}
      />
    );
  }
}

// Login Screen Component
function LoginScreen({ onLogin }) {
  const [loginType, setLoginType] = useState('coach');
  const [coachCredentials, setCoachCredentials] = useState({ username: '', password: '' });
  const [clientId, setClientId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCoachLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/coach/login`, null, {
        params: coachCredentials
      });
      
      onLogin(response.data.user, 'coach', response.data.access_token);
    } catch (error) {
      setError('Invalid coach credentials');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClientLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/client/login`, null, {
        params: { client_id: clientId }
      });
      
      onLogin(response.data.user, 'client', response.data.access_token);
    } catch (error) {
      setError('Invalid client ID');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-gray-900 text-center mb-8">🏋️ Gym Coach System</h1>
        
        {/* Login Type Selector */}
        <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setLoginType('coach')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-all ${
              loginType === 'coach'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-gray-200'
            }`}
          >
            Coach Login
          </button>
          <button
            onClick={() => setLoginType('client')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-all ${
              loginType === 'client'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-gray-200'
            }`}
          >
            Client Login
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Coach Login Form */}
        {loginType === 'coach' && (
          <form onSubmit={handleCoachLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
              <input
                type="text"
                value={coachCredentials.username}
                onChange={(e) => setCoachCredentials({...coachCredentials, username: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={coachCredentials.password}
                onChange={(e) => setCoachCredentials({...coachCredentials, password: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary"
            >
              {isLoading ? 'Logging in...' : 'Login as Coach'}
            </button>
            <p className="text-xs text-gray-500 text-center mt-2">
              Default: Username: coach, Password: coach123
            </p>
          </form>
        )}

        {/* Client Login Form */}
        {loginType === 'client' && (
          <form onSubmit={handleClientLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Client ID</label>
              <input
                type="text"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="Enter your Client ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary"
            >
              {isLoading ? 'Logging in...' : 'Login as Client'}
            </button>
            <p className="text-xs text-gray-500 text-center mt-2">
              Get your Client ID from your coach
            </p>
          </form>
        )}
      </div>
    </div>
  );
}

// Coach Dashboard Component
function CoachDashboard({ user, token, currentView, setCurrentView, onLogout }) {
  const [dashboardData, setDashboardData] = useState({});
  const [clients, setClients] = useState([]);
  const [routines, setRoutines] = useState([]);
  const [exercises, setExercises] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [progressComparison, setProgressComparison] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    loadDashboardData();
    loadClients();
    loadRoutines();
    loadExercises();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/coach/dashboard`, axiosConfig);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    }
  };

  const loadClients = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/coach/clients`, axiosConfig);
      setClients(response.data);
    } catch (error) {
      console.error('Error loading clients:', error);
    }
  };

  const loadRoutines = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/coach/routines`, axiosConfig);
      setRoutines(response.data);
    } catch (error) {
      console.error('Error loading routines:', error);
    }
  };

  const loadExercises = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/exercises`);
      setExercises(response.data);
    } catch (error) {
      console.error('Error loading exercises:', error);
    }
  };

  const loadProgressComparison = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/coach/progress-comparison`, axiosConfig);
      setProgressComparison(response.data);
    } catch (error) {
      console.error('Error loading progress comparison:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">🏋️ Coach Dashboard</h1>
            <div className="flex items-center gap-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    currentView === 'dashboard'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setCurrentView('clients')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    currentView === 'clients'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Clients
                </button>
                <button
                  onClick={() => setCurrentView('routines')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    currentView === 'routines'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Routines
                </button>
                <button
                  onClick={() => {
                    setCurrentView('comparison');
                    loadProgressComparison();
                  }}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    currentView === 'comparison'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Progress
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Welcome, {user.name}</span>
                <button onClick={onLogout} className="text-sm text-red-600 hover:text-red-800">
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Dashboard Overview */}
        {currentView === 'dashboard' && (
          <DashboardOverview 
            data={dashboardData} 
            clients={clients}
            token={token}
            setSelectedClient={setSelectedClient}
            setCurrentView={setCurrentView}
          />
        )}

        {/* Clients Management */}
        {currentView === 'clients' && (
          <ClientsManagement 
            clients={clients}
            token={token}
            onClientsUpdate={loadClients}
            selectedClient={selectedClient}
            setSelectedClient={setSelectedClient}
          />
        )}

        {/* Routines Management */}
        {currentView === 'routines' && (
          <RoutinesManagement 
            routines={routines}
            exercises={exercises}
            clients={clients}
            token={token}
            onRoutinesUpdate={loadRoutines}
          />
        )}

        {/* Progress Comparison */}
        {currentView === 'comparison' && (
          <ProgressComparison 
            data={progressComparison}
            isLoading={isLoading}
            token={token}
          />
        )}
      </div>
    </div>
  );
}

// Dashboard Overview Component
function DashboardOverview({ data, clients, token, setSelectedClient, setCurrentView }) {
  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="text-3xl font-bold text-blue-600">{data.total_clients || 0}</div>
          <div className="text-sm text-gray-600">Total Clients</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="text-3xl font-bold text-green-600">{data.total_workouts_this_week || 0}</div>
          <div className="text-sm text-gray-600">Workouts This Week</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="text-3xl font-bold text-purple-600">{data.active_routines || 0}</div>
          <div className="text-sm text-gray-600">Active Routines</div>
        </div>
      </div>

      {/* Recent Clients */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Clients</h2>
        <div className="space-y-3">
          {clients.slice(0, 5).map(client => (
            <div key={client.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">{client.name}</div>
                <div className="text-sm text-gray-500">{client.email}</div>
              </div>
              <button
                onClick={() => {
                  setSelectedClient(client);
                  setCurrentView('clients');
                }}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View Progress
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Client Management Component
function ClientsManagement({ clients, token, onClientsUpdate, selectedClient, setSelectedClient }) {
  const [showAddClient, setShowAddClient] = useState(false);
  const [newClient, setNewClient] = useState({ name: '', email: '' });
  const [clientProgress, setClientProgress] = useState(null);
  const [showMeasurements, setShowMeasurements] = useState(false);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const addClient = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/api/coach/clients`, null, {
        ...axiosConfig,
        params: newClient
      });
      setNewClient({ name: '', email: '' });
      setShowAddClient(false);
      onClientsUpdate();
      alert('Client added successfully!');
    } catch (error) {
      alert('Error adding client');
    }
  };

  const loadClientProgress = async (clientId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/coach/client/${clientId}/progress`, axiosConfig);
      setClientProgress(response.data);
    } catch (error) {
      console.error('Error loading client progress:', error);
    }
  };

  useEffect(() => {
    if (selectedClient) {
      loadClientProgress(selectedClient.id);
    }
  }, [selectedClient]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Clients List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Clients</h2>
          <button
            onClick={() => setShowAddClient(true)}
            className="btn-primary text-sm"
          >
            Add Client
          </button>
        </div>

        {showAddClient && (
          <form onSubmit={addClient} className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="space-y-3">
              <input
                type="text"
                placeholder="Client Name"
                value={newClient.name}
                onChange={(e) => setNewClient({...newClient, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                required
              />
              <input
                type="email"
                placeholder="Email (optional)"
                value={newClient.email}
                onChange={(e) => setNewClient({...newClient, email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <div className="flex gap-2">
                <button type="submit" className="btn-primary text-sm">Add</button>
                <button
                  type="button"
                  onClick={() => setShowAddClient(false)}
                  className="btn-secondary text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </form>
        )}

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {clients.map(client => (
            <div
              key={client.id}
              onClick={() => setSelectedClient(client)}
              className={`p-3 rounded-lg border cursor-pointer transition-all ${
                selectedClient && selectedClient.id === client.id
                  ? 'border-blue-300 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="font-medium text-gray-900">{client.name}</div>
              <div className="text-sm text-gray-500">ID: {client.id.slice(0, 8)}...</div>
            </div>
          ))}
        </div>
      </div>

      {/* Client Progress */}
      <div className="lg:col-span-2">
        {selectedClient && clientProgress ? (
          <ClientProgressView 
            client={selectedClient}
            progress={clientProgress}
            token={token}
            showMeasurements={showMeasurements}
            setShowMeasurements={setShowMeasurements}
            onProgressUpdate={() => loadClientProgress(selectedClient.id)}
          />
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <p className="text-gray-500 text-center py-8">Select a client to view progress</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Client Progress View Component
function ClientProgressView({ client, progress, token, showMeasurements, setShowMeasurements, onProgressUpdate }) {
  const [newMeasurement, setNewMeasurement] = useState({
    weight_kg: '',
    body_fat_percentage: '',
    measurements: {
      chest: '',
      waist: '',
      arms: '',
      thighs: '',
      shoulders: ''
    }
  });

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const addMeasurement = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/api/coach/measurements/${client.id}`, newMeasurement, axiosConfig);
      setNewMeasurement({
        weight_kg: '',
        body_fat_percentage: '',
        measurements: {
          chest: '',
          waist: '',
          arms: '',
          thighs: '',
          shoulders: ''
        }
      });
      setShowMeasurements(false);
      onProgressUpdate();
      alert('Measurements added successfully!');
    } catch (error) {
      alert('Error adding measurements');
    }
  };

  return (
    <div className="space-y-6">
      {/* Client Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{client.name}</h2>
            <p className="text-sm text-gray-500">Client ID: {client.id.slice(0, 8)}...</p>
          </div>
          <button
            onClick={() => setShowMeasurements(true)}
            className="btn-primary text-sm"
          >
            Add Measurements
          </button>
        </div>
      </div>

      {/* Add Measurements Modal */}
      {showMeasurements && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Body Measurements</h3>
          <form onSubmit={addMeasurement} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Weight (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  value={newMeasurement.weight_kg}
                  onChange={(e) => setNewMeasurement({...newMeasurement, weight_kg: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Body Fat %</label>
                <input
                  type="number"
                  step="0.1"
                  value={newMeasurement.body_fat_percentage}
                  onChange={(e) => setNewMeasurement({...newMeasurement, body_fat_percentage: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.keys(newMeasurement.measurements).map(part => (
                <div key={part}>
                  <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">{part} (cm)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={newMeasurement.measurements[part]}
                    onChange={(e) => setNewMeasurement({
                      ...newMeasurement,
                      measurements: {
                        ...newMeasurement.measurements,
                        [part]: e.target.value
                      }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              ))}
            </div>
            
            <div className="flex gap-2">
              <button type="submit" className="btn-primary">Add Measurements</button>
              <button
                type="button"
                onClick={() => setShowMeasurements(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Exercise Stats */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Exercise Progress</h3>
        <div className="space-y-4">
          {Object.values(progress.exercise_stats).map(stat => (
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

      {/* Recent Measurements */}
      {progress.measurements.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Body Measurements History</h3>
          <div className="space-y-3">
            {progress.measurements.slice(0, 5).map((measurement, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-gray-500">
                    {new Date(measurement.date).toLocaleDateString()}
                  </div>
                  <div className="text-sm font-medium">
                    {measurement.weight_kg && `${measurement.weight_kg}kg`}
                    {measurement.body_fat_percentage && ` | ${measurement.body_fat_percentage}% BF`}
                  </div>
                </div>
                {measurement.measurements && Object.keys(measurement.measurements).length > 0 && (
                  <div className="grid grid-cols-3 gap-2 text-xs text-gray-600">
                    {Object.entries(measurement.measurements).map(([part, value]) => (
                      value && <div key={part}>{part}: {value}cm</div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Routines Management Component
function RoutinesManagement({ routines, exercises, clients, token, onRoutinesUpdate }) {
  const [showCreateRoutine, setShowCreateRoutine] = useState(false);
  const [newRoutine, setNewRoutine] = useState({
    name: '',
    exercises: [],
    assigned_clients: []
  });

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  const createRoutine = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/api/coach/routines`, newRoutine, axiosConfig);
      setNewRoutine({
        name: '',
        exercises: [],
        assigned_clients: []
      });
      setShowCreateRoutine(false);
      onRoutinesUpdate();
      alert('Routine created successfully!');
    } catch (error) {
      alert('Error creating routine');
    }
  };

  const addExerciseToRoutine = (exercise) => {
    const routineExercise = {
      exercise_id: exercise.id,
      exercise_name: exercise.name,
      target_sets: 3,
      target_reps: "8-12",
      target_weight: null,
      rest_seconds: 90
    };
    setNewRoutine({
      ...newRoutine,
      exercises: [...newRoutine.exercises, routineExercise]
    });
  };

  return (
    <div className="space-y-6">
      {/* Create Routine */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Workout Routines</h2>
          <button
            onClick={() => setShowCreateRoutine(true)}
            className="btn-primary"
          >
            Create Routine
          </button>
        </div>

        {showCreateRoutine && (
          <div className="border-t pt-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Routine</h3>
            <form onSubmit={createRoutine} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Routine Name</label>
                <input
                  type="text"
                  value={newRoutine.name}
                  onChange={(e) => setNewRoutine({...newRoutine, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  required
                />
              </div>

              {/* Exercise Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Add Exercises</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-40 overflow-y-auto border rounded-lg p-2">
                  {exercises.map(exercise => (
                    <button
                      key={exercise.id}
                      type="button"
                      onClick={() => addExerciseToRoutine(exercise)}
                      className="text-left p-2 rounded border hover:bg-gray-50"
                    >
                      <div className="font-medium">{exercise.name}</div>
                      <div className="text-sm text-gray-500">{exercise.muscle_group}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Selected Exercises */}
              {newRoutine.exercises.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Selected Exercises</label>
                  <div className="space-y-2">
                    {newRoutine.exercises.map((exercise, index) => (
                      <div key={index} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">{exercise.exercise_name}</div>
                        </div>
                        <div className="flex gap-2">
                          <input
                            type="number"
                            placeholder="Sets"
                            value={exercise.target_sets}
                            onChange={(e) => {
                              const updated = [...newRoutine.exercises];
                              updated[index].target_sets = parseInt(e.target.value) || 3;
                              setNewRoutine({...newRoutine, exercises: updated});
                            }}
                            className="w-16 px-2 py-1 border rounded text-sm"
                          />
                          <input
                            type="text"
                            placeholder="Reps"
                            value={exercise.target_reps}
                            onChange={(e) => {
                              const updated = [...newRoutine.exercises];
                              updated[index].target_reps = e.target.value;
                              setNewRoutine({...newRoutine, exercises: updated});
                            }}
                            className="w-20 px-2 py-1 border rounded text-sm"
                          />
                          <button
                            type="button"
                            onClick={() => {
                              const updated = newRoutine.exercises.filter((_, i) => i !== index);
                              setNewRoutine({...newRoutine, exercises: updated});
                            }}
                            className="text-red-500 hover:text-red-700 p-1"
                          >
                            ✕
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Assign to Clients */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Assign to Clients</label>
                <div className="space-y-2 max-h-32 overflow-y-auto border rounded-lg p-2">
                  {clients.map(client => (
                    <label key={client.id} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={newRoutine.assigned_clients.includes(client.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewRoutine({
                              ...newRoutine,
                              assigned_clients: [...newRoutine.assigned_clients, client.id]
                            });
                          } else {
                            setNewRoutine({
                              ...newRoutine,
                              assigned_clients: newRoutine.assigned_clients.filter(id => id !== client.id)
                            });
                          }
                        }}
                        className="mr-2"
                      />
                      {client.name}
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <button type="submit" className="btn-primary">Create Routine</button>
                <button
                  type="button"
                  onClick={() => setShowCreateRoutine(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Existing Routines */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Existing Routines</h3>
        <div className="space-y-4">
          {routines.map(routine => (
            <div key={routine.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-gray-900">{routine.name}</div>
                <div className="text-sm text-gray-500">
                  {routine.assigned_clients.length} clients assigned
                </div>
              </div>
              <div className="text-sm text-gray-600 mb-2">
                {routine.exercises.length} exercises
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {routine.exercises.map((exercise, index) => (
                  <div key={index} className="text-sm bg-gray-50 rounded p-2">
                    <span className="font-medium">{exercise.exercise_name}</span> - 
                    {exercise.target_sets} sets × {exercise.target_reps} reps
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Progress Comparison Component
function ProgressComparison({ data, isLoading, token }) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="text-center py-8">Loading progress comparison...</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Client Progress Comparison</h2>
      
      <div className="space-y-6">
        {data.map(clientData => (
          <div key={clientData.client.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">{clientData.client.name}</h3>
              <div className="text-sm text-gray-500">
                {clientData.workouts_this_month} workouts this month
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Latest Weight */}
              <div className="bg-blue-50 rounded-lg p-3">
                <div className="text-sm text-gray-600">Latest Weight</div>
                <div className="text-lg font-semibold text-blue-600">
                  {clientData.latest_measurement?.weight_kg || 'N/A'} 
                  {clientData.latest_measurement?.weight_kg && 'kg'}
                </div>
              </div>
              
              {/* Total Volume */}
              <div className="bg-green-50 rounded-lg p-3">
                <div className="text-sm text-gray-600">Total Volume (Month)</div>
                <div className="text-lg font-semibold text-green-600">
                  {clientData.total_volume_this_month}kg
                </div>
              </div>
              
              {/* Body Fat */}
              <div className="bg-purple-50 rounded-lg p-3">
                <div className="text-sm text-gray-600">Body Fat %</div>
                <div className="text-lg font-semibold text-purple-600">
                  {clientData.latest_measurement?.body_fat_percentage || 'N/A'}
                  {clientData.latest_measurement?.body_fat_percentage && '%'}
                </div>
              </div>
            </div>
            
            {/* Latest Measurements */}
            {clientData.latest_measurement?.measurements && (
              <div className="mt-4">
                <div className="text-sm text-gray-600 mb-2">Latest Measurements (cm)</div>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-xs">
                  {Object.entries(clientData.latest_measurement.measurements).map(([part, value]) => (
                    value && (
                      <div key={part} className="bg-gray-50 rounded p-2">
                        <div className="font-medium capitalize">{part}</div>
                        <div>{value}cm</div>
                      </div>
                    )
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Client Interface Component
function ClientInterface({ user, token, onLogout }) {
  const [routine, setRoutine] = useState(null);
  const [currentWorkout, setCurrentWorkout] = useState([]);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [workoutHistory, setWorkoutHistory] = useState([]);
  const [currentView, setCurrentView] = useState('routine');

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    loadRoutine();
    loadWorkoutHistory();
  }, []);

  const loadRoutine = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/client/routine`, axiosConfig);
      setRoutine(response.data.routine);
    } catch (error) {
      console.error('Error loading routine:', error);
    }
  };

  const loadWorkoutHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/client/workouts`, axiosConfig);
      setWorkoutHistory(response.data);
    } catch (error) {
      console.error('Error loading workout history:', error);
    }
  };

  const startWorkout = () => {
    if (!routine) return;
    
    const workoutExercises = routine.exercises.map(exercise => ({
      exercise_id: exercise.exercise_id,
      exercise_name: exercise.exercise_name,
      target_sets: exercise.target_sets,
      target_reps: exercise.target_reps,
      tips: exercise.tips,
      sets: []
    }));
    
    setCurrentWorkout(workoutExercises);
    setCurrentView('workout');
  };

  const saveWorkout = async () => {
    if (currentWorkout.length === 0) return;

    try {
      const workoutData = {
        routine_id: routine.id,
        routine_name: routine.name,
        exercises: currentWorkout.map(ex => ({
          exercise_id: ex.exercise_id,
          exercise_name: ex.exercise_name,
          sets: ex.sets
        }))
      };

      await axios.post(`${API_BASE_URL}/api/client/workouts`, workoutData, axiosConfig);
      setCurrentWorkout([]);
      setSelectedExercise(null);
      setCurrentView('routine');
      loadWorkoutHistory();
      alert('Workout saved successfully!');
    } catch (error) {
      alert('Error saving workout');
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">🏋️ My Workout</h1>
            <div className="flex items-center gap-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentView('routine')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    currentView === 'routine'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  My Routine
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
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Welcome, {user.name}</span>
                <button onClick={onLogout} className="text-sm text-red-600 hover:text-red-800">
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Routine View */}
        {currentView === 'routine' && (
          <div className="space-y-6">
            {routine ? (
              <>
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900">{routine.name}</h2>
                    <button onClick={startWorkout} className="btn-primary">
                      Start Workout
                    </button>
                  </div>
                  
                  <div className="space-y-3">
                    {routine.exercises.map((exercise, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-medium text-gray-900">{exercise.exercise_name}</div>
                          <div className="text-sm text-gray-500">
                            {exercise.target_sets} sets × {exercise.target_reps} reps
                          </div>
                        </div>
                        {exercise.tips && (
                          <div className="text-sm text-blue-600 bg-blue-50 rounded p-2">
                            💡 {exercise.tips}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <p className="text-gray-500 text-center py-8">No routine assigned. Contact your coach.</p>
              </div>
            )}
          </div>
        )}

        {/* Workout View */}
        {currentView === 'workout' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Exercise List */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Exercises</h2>
              <div className="space-y-2">
                {currentWorkout.map((exercise, index) => (
                  <div
                    key={index}
                    onClick={() => setSelectedExercise(exercise)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      selectedExercise && selectedExercise.exercise_id === exercise.exercise_id
                        ? 'border-blue-300 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{exercise.exercise_name}</div>
                    <div className="text-sm text-gray-500">
                      {exercise.sets.length}/{exercise.target_sets} sets
                    </div>
                  </div>
                ))}
              </div>
              
              <button
                onClick={saveWorkout}
                className="w-full btn-primary mt-4"
              >
                Save Workout
              </button>
            </div>

            {/* Exercise Details */}
            <div className="lg:col-span-2">
              {selectedExercise ? (
                <ClientSetLogger
                  exercise={selectedExercise}
                  onUpdateSets={(sets) => updateExerciseSets(selectedExercise.exercise_id, sets)}
                />
              ) : (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <p className="text-gray-500 text-center py-8">Select an exercise to start logging</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* History View */}
        {currentView === 'history' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Workout History</h2>
            
            {workoutHistory.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No workouts completed yet</p>
            ) : (
              <div className="space-y-4">
                {workoutHistory.map(workout => (
                  <div key={workout.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="text-lg font-medium text-gray-900">
                        {new Date(workout.date).toLocaleDateString()}
                      </div>
                      <div className="text-sm text-gray-500">
                        {workout.routine_name} • {workout.exercises.length} exercises
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
      </div>
    </div>
  );
}

// Client Set Logger Component
function ClientSetLogger({ exercise, onUpdateSets }) {
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
      reps: sets.length > 0 ? sets[sets.length - 1].reps : parseInt(exercise.target_reps.split('-')[0]) || 8,
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
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">{exercise.exercise_name}</h3>
          <div className="text-sm text-gray-500">
            Target: {exercise.target_sets} sets × {exercise.target_reps} reps
          </div>
        </div>
        <button
          onClick={addSet}
          disabled={sets.length >= exercise.target_sets}
          className="btn-secondary text-sm"
        >
          Add Set
        </button>
      </div>

      {exercise.tips && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-sm text-blue-800">
            <strong>💡 Form Tips:</strong> {exercise.tips}
          </div>
        </div>
      )}

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