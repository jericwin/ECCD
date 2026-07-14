import React from 'react';

export const HealthMonitor = () => {
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Health Monitoring</h2>
      <p style={{ color: '#64748b' }}>Track BMI computations and DOH Extended Program on Immunization schedules.</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginTop: '30px' }}>
        <div style={{ padding: '20px', border: '1px solid #cbd5e1', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 10px 0' }}>BMI Tracking</h3>
          <p style={{ fontSize: '14px', color: '#64748b', margin: '0 0 20px 0' }}>
            Record height & weight metrics. Automatically compute WHO Child Growth Standard percentiles.
          </p>
          <button style={{
            padding: '8px 12px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Manage BMI Records
          </button>
        </div>

        <div style={{ padding: '20px', border: '1px solid #cbd5e1', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 10px 0' }}>Immunization Logs</h3>
          <p style={{ fontSize: '14px', color: '#64748b', margin: '0 0 20px 0' }}>
            Log vaccine doses given to learners. Compare against schedules to flag overdue immunizations.
          </p>
          <button style={{
            padding: '8px 12px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Manage Immunization Records
          </button>
        </div>
      </div>
    </div>
  );
};
export default HealthMonitor;
