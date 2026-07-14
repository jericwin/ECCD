import React from 'react';

export const Announcements = () => {
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Announcements Board</h2>
      <p style={{ color: '#64748b' }}>Post notices and broadcast messages to parents.</p>
      
      <div style={{ marginTop: '20px' }}>
        <button style={{
          padding: '10px 15px',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          fontWeight: 'bold',
          cursor: 'pointer'
        }}>
          Create Announcement
        </button>
      </div>

      <div style={{ marginTop: '30px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ padding: '20px', border: '1px solid #cbd5e1', borderRadius: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
            <h3 style={{ margin: 0, fontSize: '18px' }}>Welcome to School Year 2026-2027</h3>
            <span style={{ fontSize: '12px', color: '#64748b' }}>2 hours ago</span>
          </div>
          <p style={{ margin: 0, color: '#334155', lineHeight: 1.5 }}>
            Welcome parents and learners! We are looking forward to a fantastic year of early development, learning and fun. Classes begin next Monday.
          </p>
          <div style={{ marginTop: '15px', fontSize: '12px', color: '#64748b' }}>
            Posted by: Teacher Mary
          </div>
        </div>
      </div>
    </div>
  );
};
export default Announcements;
