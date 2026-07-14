import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './providers/AuthProvider';
import { MainLayout } from './components/layout/MainLayout';

// Feature Views
import { Login } from './features/auth/Login';
import { Register } from './features/auth/Register';
import { Dashboard } from './features/dashboard/Dashboard';
import { ClassroomList } from './features/classrooms/ClassroomList';
import { LearnerList } from './features/learners/LearnerList';
import { HealthMonitor } from './features/health/HealthMonitor';
import { Reports } from './features/reports/Reports';
import { Announcements } from './features/announcements/Announcements';
import { Settings } from './features/settings/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'sans-serif' }}>Loading system foundation...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Shell Layout Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="classrooms" element={<ClassroomList />} />
              <Route path="learners" element={<LearnerList />} />
              <Route path="health" element={<HealthMonitor />} />
              <Route path="reports" element={<Reports />} />
              <Route path="announcements" element={<Announcements />} />
              <Route path="settings" element={<Settings />} />
              
              {/* Fallback routes for parent specific features if requested */}
              <Route path="child-profile" element={<div>Juanita Dela Cruz - Age 4, Kindergarten B. Healthy BMI.</div>} />
              <Route path="child-health" element={<div>BMI: 15.2 (Normal). DOH Vaccines completed: BCS, HepB, DPT 1-3.</div>} />
            </Route>

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
