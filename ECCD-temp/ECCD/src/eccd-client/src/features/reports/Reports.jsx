import React from 'react';

export const Reports = () => {
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Analytics Reports</h2>
      <p style={{ color: '#64748b' }}>Generate printable growth reports, attendance logs, and classroom summaries.</p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '20px', maxWidth: '400px' }}>
        <div style={{ padding: '15px', border: '1px solid #cbd5e1', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h4 style={{ margin: '0 0 5px 0' }}>Class Growth Summary</h4>
            <span style={{ fontSize: '12px', color: '#64748b' }}>PDF document for DOH submit</span>
          </div>
          <button style={{ padding: '6px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer' }}>
            Export
          </button>
        </div>

        <div style={{ padding: '15px', border: '1px solid #cbd5e1', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h4 style={{ margin: '0 0 5px 0' }}>Attendance Risk Trend</h4>
            <span style={{ fontSize: '12px', color: '#64748b' }}>Predictive list of at-risk students</span>
          </div>
          <button style={{ padding: '6px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer' }}>
            Export
          </button>
        </div>
      </div>
    </div>
  );
};
export default Reports;
