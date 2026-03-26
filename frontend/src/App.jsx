import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import ChatInterface from './components/ChatInterface';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Onboarding from './pages/Onboarding';
import MyAlerts from './pages/MyAlerts';
import Schemes from './pages/Schemes';
import FactChecker from './pages/FactChecker';
import ReportIssue from './pages/ReportIssue';
import MyReports from './pages/MyReports';
import Profile from './pages/Profile';
import Government from './pages/Government';
import GovernmentDashboard from './pages/GovernmentDashboard';
import ReportDetail from './pages/ReportDetail';
import PredictionDetail from './pages/PredictionDetail';
import AllPredictions from './pages/AllPredictions';
import CitizenReports from './pages/CitizenReports';
import Analytics from './pages/Analytics';

const GOVERNMENT_ROLES = ['government', 'gov'];

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" />;
  }

  return children;
};

function AppContent() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <Onboarding />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/alerts"
          element={
            <ProtectedRoute>
              <MyAlerts />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/schemes"
          element={
            <ProtectedRoute>
              <Schemes />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        
        <Route path="/fact-check" element={<FactChecker />} />
        
        <Route
          path="/report"
          element={
            <ProtectedRoute>
              <ReportIssue />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/my-reports"
          element={
            <ProtectedRoute>
              <MyReports />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/government"
          element={
            <ProtectedRoute allowedRoles={GOVERNMENT_ROLES}>
              <Navigate to="/government/dashboard" replace />
            </ProtectedRoute>
          }
        />

        <Route
          path="/government/dashboard"
          element={
            <ProtectedRoute allowedRoles={GOVERNMENT_ROLES}>
              <GovernmentDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/government/command-center"
          element={
            <ProtectedRoute allowedRoles={GOVERNMENT_ROLES}>
              <Government />
            </ProtectedRoute>
          }
        />

        <Route
          path="/government/predictions"
          element={
            <ProtectedRoute allowedRoles={GOVERNMENT_ROLES}>
              <AllPredictions />
            </ProtectedRoute>
          }
        />

        <Route
          path="/government/prediction/:id"
          element={
            <ProtectedRoute allowedRoles={GOVERNMENT_ROLES}>
              <PredictionDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/government/reports"
          element={
            <ProtectedRoute allowedRoles={GOVERNMENT_ROLES}>
              <CitizenReports />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/:id"
          element={
            <ProtectedRoute allowedRoles={GOVERNMENT_ROLES}>
              <ReportDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/government/analytics"
          element={
            <ProtectedRoute allowedRoles={GOVERNMENT_ROLES}>
              <Analytics />
            </ProtectedRoute>
          }
        />
      </Routes>
      
      {isAuthenticated && <ChatInterface />}
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;