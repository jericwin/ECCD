import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../providers/AuthProvider';

export const MainLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      {/* Sidebar Navigation */}
      <aside style={{
        width: '260px',
        backgroundColor: '#1e293b',
        color: '#f8fafc',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '30px', color: '#38bdf8' }}>
            ECCD Monitor
          </div>
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <Link to="/" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
              Dashboard
            </Link>
            
            {user?.role === 'Administrator' || user?.role === 'Teacher' ? (
              <>
                <Link to="/classrooms" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
                  My Classrooms
                </Link>
                <Link to="/learners" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
                  My Learners
                </Link>
                <Link to="/health" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
                  Health Monitoring
                </Link>
                <Link to="/reports" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
                  Reports
                </Link>
              </>
            ) : (
              <>
                <Link to="/child-profile" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
                  My Child
                </Link>
                <Link to="/child-health" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
                  BMI & Vaccines
                </Link>
              </>
            )}
            
            <Link to="/announcements" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
              Announcements
            </Link>
            <Link to="/settings" style={{ color: '#cbd5e1', textDecoration: 'none', padding: '8px', borderRadius: '4px' }}>
              Settings
            </Link>
          </nav>
        </div>

        {/* User profile section in sidebar */}
        <div style={{ borderTop: '1px solid #334155', paddingTop: '15px' }}>
          <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{user?.firstName} {user?.lastName}</div>
          <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '10px' }}>{user?.role}</div>
          <button
            onClick={handleLogout}
            style={{
              width: '100%',
              padding: '8px',
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, backgroundColor: '#f1f5f9', padding: '30px' }}>
        <header style={{
          backgroundColor: 'white',
          padding: '15px 30px',
          borderRadius: '8px',
          marginBottom: '30px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <h1 style={{ fontSize: '20px', margin: 0, color: '#0f172a' }}>Early Childhood Development Monitor</h1>
          <div style={{ color: '#64748b', fontSize: '14px' }}>
            Welcome back, {user?.userName}!
          </div>
        </header>

        {/* Viewport for subroutes */}
        <div style={{
          backgroundColor: 'white',
          padding: '30px',
          borderRadius: '8px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          minHeight: 'calc(100vh - 180px)'
        }}>
          <Outlet />
        </div>
      </main>
    </div>
  );
};
