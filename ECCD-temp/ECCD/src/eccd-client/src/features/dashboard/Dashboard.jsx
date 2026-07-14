import React from 'react';

export const Dashboard = () => {
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Dashboard Overview</h2>
      <p>Welcome to the early childhood development monitoring system.</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginTop: '20px' }}>
        <div style={{ padding: '20px', border: '1px solid #e2e8f0', borderRadius: '6px', backgroundColor: '#f8fafc' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#0f172a' }}>Total Learners</h3>
          <p style={{ fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#38bdf8' }}>0</p>
          <span style={{ fontSize: '12px', color: '#64748b' }}>Active enrollments across classes</span>
        </div>

        <div style={{ padding: '20px', border: '1px solid #e2e8f0', borderRadius: '6px', backgroundColor: '#f8fafc' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#0f172a' }}>Nutritional Flags</h3>
          <p style={{ fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#ef4444' }}>0</p>
          <span style={{ fontSize: '12px', color: '#64748b' }}>Learners flagged as underweight/obese</span>
        </div>

        <div style={{ padding: '20px', border: '1px solid #e2e8f0', borderRadius: '6px', backgroundColor: '#f8fafc' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#0f172a' }}>Vaccination Coverage</h3>
          <p style={{ fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#22c55e' }}>100%</p>
          <span style={{ fontSize: '12px', color: '#64748b' }}>Overdue vaccines pending</span>
        </div>
      </div>

      <div style={{ marginTop: '40px', padding: '20px', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
        <h3>Recent Classroom Updates</h3>
        <p style={{ color: '#64748b' }}>No recent updates from classrooms.</p>
      </div>
    </div>
  );
};
export default Dashboard;
