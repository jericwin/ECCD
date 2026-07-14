import React from 'react';
import { useAuth } from '../../providers/AuthProvider';

export const Settings = () => {
  const { user } = useAuth();

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>System Settings</h2>
      <p style={{ color: '#64748b' }}>Configure your profile preferences and system permissions.</p>

      <div style={{ marginTop: '30px', maxWidth: '500px' }}>
        <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '20px', marginBottom: '20px' }}>
          <h3 style={{ margin: '0 0 15px 0' }}>Profile Details</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '10px 15px', fontSize: '14px' }}>
            <span style={{ fontWeight: 'bold' }}>Username:</span>
            <span>{user?.userName}</span>

            <span style={{ fontWeight: 'bold' }}>Email Address:</span>
            <span>{user?.email}</span>

            <span style={{ fontWeight: 'bold' }}>Full Name:</span>
            <span>{user?.firstName} {user?.lastName}</span>

            <span style={{ fontWeight: 'bold' }}>Account Role:</span>
            <span>{user?.role}</span>
          </div>
        </div>

        <div>
          <h3 style={{ margin: '0 0 15px 0' }}>Change Password</h3>
          <form style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Current Password</label>
              <input type="password" style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px' }} />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>New Password</label>
              <input type="password" style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px' }} />
            </div>
            <button type="button" style={{
              alignSelf: 'flex-start',
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>
              Update Password
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
export default Settings;
