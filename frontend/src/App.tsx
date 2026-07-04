import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import DashboardLayout from './layouts/DashboardLayout';
import Login from './pages/Login';
import ChangePassword from './pages/ChangePassword';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Documents from './pages/Documents';
import Analytics from './pages/Admin/Analytics';
import Users from './pages/Admin/Users';

const ProtectedRoute = ({ children, requireAdmin = false, skipPasswordCheck = false }: { children: React.ReactNode, requireAdmin?: boolean, skipPasswordCheck?: boolean }) => {
  const { accessToken, user } = useAuthStore();
  
  if (!accessToken) return <Navigate to="/login" replace />;
  
  // If user is forced to change password and this isn't the change-password route, redirect
  if (!skipPasswordCheck && user?.force_password_change) {
    return <Navigate to="/change-password" replace />;
  }

  // If this IS the change-password route but they don't need to change it, redirect to dashboard
  if (skipPasswordCheck && !user?.force_password_change) {
    return <Navigate to="/dashboard" replace />;
  }

  if (requireAdmin && user?.role !== 'Admin') return <Navigate to="/dashboard" replace />;
  
  return <>{children}</>;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/change-password" element={
          <ProtectedRoute skipPasswordCheck>
            <ChangePassword />
          </ProtectedRoute>
        } />
        
        <Route path="/" element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="documents" element={<Documents />} />
          
          <Route path="admin/analytics" element={
            <ProtectedRoute requireAdmin>
              <Analytics />
            </ProtectedRoute>
          } />
          
          <Route path="admin/users" element={
            <ProtectedRoute requireAdmin>
              <Users />
            </ProtectedRoute>
          } />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
