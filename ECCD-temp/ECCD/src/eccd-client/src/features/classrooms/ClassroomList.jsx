import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';

export const ClassroomList = () => {
  const [classrooms, setClassrooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Modal states
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [subject, setSubject] = useState(7); // Default General
  const [description, setDescription] = useState('');
  const [ageGroup, setAgeGroup] = useState('');
  const [schoolYear, setSchoolYear] = useState('2026-2027');
  const [schedule, setSchedule] = useState('');
  const [themeColor, setThemeColor] = useState('#4CAF50');
  const [maxLearners, setMaxLearners] = useState(25);
  const [submitLoading, setSubmitLoading] = useState(false);

  const fetchClassrooms = async () => {
    try {
      setLoading(true);
      const response = await api.get('/classrooms');
      if (response.data?.data) {
        setClassrooms(response.data.data);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to load classrooms list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClassrooms();
  }, []);

  const handleCreateClassroom = async (e) => {
    e.preventDefault();
    if (!name) return;

    setSubmitLoading(true);
    try {
      await api.post('/classrooms', {
        name,
        subject,
        description,
        ageGroup,
        schoolYear,
        schedule,
        themeColor,
        maxLearners
      });

      // Clear states & close modal
      setName('');
      setSubject(7);
      setDescription('');
      setAgeGroup('');
      setSchedule('');
      setThemeColor('#4CAF50');
      setMaxLearners(25);
      setShowModal(false);

      // Refresh list
      fetchClassrooms();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error?.message || 'Failed to create classroom.');
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleArchiveClassroom = async (id) => {
    if (!confirm('Are you sure you want to archive this classroom?')) return;

    try {
      await api.delete(`/classrooms/${id}`);
      fetchClassrooms();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error?.message || 'Failed to archive classroom.');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 0 }}>
        <div>
          <h2 style={{ margin: 0 }}>Classrooms Management</h2>
          <p style={{ color: '#64748b', margin: '5px 0 0 0' }}>Manage early childhood development class cohorts here.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          style={{
            padding: '10px 15px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          + Create New Classroom
        </button>
      </div>

      {error && (
        <div style={{ padding: '10px', backgroundColor: '#fee2e2', color: '#ef4444', borderRadius: '4px', marginTop: '20px' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ marginTop: '40px', textAlign: 'center', color: '#64748b' }}>Loading classrooms...</div>
      ) : classrooms.length === 0 ? (
        <div style={{ marginTop: '40px', padding: '40px', textAlign: 'center', border: '1px dashed #cbd5e1', borderRadius: '8px', color: '#64748b' }}>
          No classrooms registered yet. Click the button above to create one.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px', marginTop: '30px' }}>
          {classrooms.map((c) => (
            <div
              key={c.id}
              style={{
                borderLeft: `6px solid ${c.themeColor || '#4CAF50'}`,
                borderTop: '1px solid #cbd5e1',
                borderRight: '1px solid #cbd5e1',
                borderBottom: '1px solid #cbd5e1',
                borderRadius: '8px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                backgroundColor: 'white',
                boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <h3 style={{ margin: 0, fontSize: '18px' }}>{c.name}</h3>
                  <span style={{
                    fontSize: '11px',
                    padding: '2px 6px',
                    backgroundColor: '#e2e8f0',
                    borderRadius: '12px',
                    color: '#475569'
                  }}>
                    {c.subjectName || c.subject}
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: '#64748b', margin: '0 0 10px 0' }}>{c.description || 'No description provided.'}</p>
                <div style={{ fontSize: '13px', color: '#334155', display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '15px' }}>
                  <span><strong>Schedule:</strong> {c.schedule || 'Not specified'}</span>
                  <span><strong>Age Group:</strong> {c.ageGroup || 'Not specified'}</span>
                  <span><strong>School Year:</strong> {c.schoolYear || 'Not specified'}</span>
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #f1f5f9', paddingTop: '12px' }}>
                <span style={{ fontSize: '13px', color: '#475569' }}>
                  Enrolled: <strong>{c.enrolledCount || 0}</strong> / {c.maxLearners}
                </span>
                <button
                  onClick={() => handleArchiveClassroom(c.id)}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: '#fee2e2',
                    color: '#ef4444',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}
                >
                  Archive
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Creation Modal */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.4)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            width: '100%',
            maxWidth: '500px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            boxSizing: 'border-box'
          }}>
            <h3 style={{ margin: '0 0 20px 0' }}>Create Classroom</h3>
            <form onSubmit={handleCreateClassroom} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Classroom Name *</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                  placeholder="e.g. Nursery - Morning Session"
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Subject / Core Presets *</label>
                  <select
                    value={subject}
                    onChange={(e) => setSubject(Number(e.target.value))}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    required
                  >
                    <option value={0}>Mathematics</option>
                    <option value={1}>English</option>
                    <option value={2}>Mother Tongue</option>
                    <option value={3}>Filipino</option>
                    <option value={4}>Science</option>
                    <option value={5}>Drawing</option>
                    <option value={6}>Storytelling</option>
                    <option value={7}>General</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Max Learners *</label>
                  <input
                    type="number"
                    value={maxLearners}
                    onChange={(e) => setMaxLearners(Number(e.target.value))}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    min={1}
                    max={100}
                    required
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Age Group</label>
                  <input
                    type="text"
                    value={ageGroup}
                    onChange={(e) => setAgeGroup(e.target.value)}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    placeholder="e.g. 3-4 years old"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>School Year</label>
                  <input
                    type="text"
                    value={schoolYear}
                    onChange={(e) => setSchoolYear(e.target.value)}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    placeholder="e.g. 2026-2027"
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Schedule</label>
                  <input
                    type="text"
                    value={schedule}
                    onChange={(e) => setSchedule(e.target.value)}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    placeholder="e.g. Mon-Fri 8:00 AM - 11:00 AM"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Theme Color</label>
                  <input
                    type="color"
                    value={themeColor}
                    onChange={(e) => setThemeColor(e.target.value)}
                    style={{ width: '100%', padding: '4px', height: '38px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box', cursor: 'pointer' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box', height: '60px', resize: 'vertical' }}
                  placeholder="Cohort remarks..."
                />
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#e2e8f0',
                    color: '#0f172a',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitLoading}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    cursor: submitLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {submitLoading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default ClassroomList;
