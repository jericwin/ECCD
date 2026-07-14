import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';

export const LearnerList = () => {
  const [learners, setLearners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');
  
  // Registration data sources
  const [parents, setParents] = useState([]);
  const [cdcs, setCdcs] = useState([]);
  const [classrooms, setClassrooms] = useState([]);

  // Modals
  const [showRegModal, setShowRegModal] = useState(false);
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [selectedLearner, setSelectedLearner] = useState(null);

  // Registration states
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [birthdate, setBirthdate] = useState('');
  const [gender, setGender] = useState(0); // 0 Male, 1 Female
  const [learnerIdCode, setLearnerIdCode] = useState('');
  const [parentId, setParentId] = useState('');
  const [cdcId, setCdcId] = useState('');
  const [regLoading, setRegLoading] = useState(false);

  // Enrollment states
  const [classroomId, setClassroomId] = useState('');
  const [enrollLoading, setEnrollLoading] = useState(false);

  const fetchLearners = async (query = '') => {
    try {
      setLoading(true);
      const url = query ? `/learners?searchQuery=${encodeURIComponent(query)}` : '/learners';
      const response = await api.get(url);
      if (response.data?.data?.items) {
        setLearners(response.data.data.items);
      }
    } catch (err) {
      console.error('Failed to load learners list', err);
      setError('Failed to load learners list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLearners();
    
    // Load metadata dependencies
    api.get('/parents').then(res => {
      if (res.data?.data) {
        setParents(res.data.data);
        if (res.data.data.length > 0) {
          setParentId(res.data.data[0].id);
        }
      }
    }).catch(e => console.error('Failed to fetch parents', e));

    api.get('/cdc').then(res => {
      if (res.data?.data) {
        setCdcs(res.data.data);
        if (res.data.data.length > 0) {
          setCdcId(res.data.data[0].id);
        }
      }
    }).catch(e => console.error('Failed to fetch CDCs', e));

    api.get('/classrooms').then(res => {
      if (res.data?.data) {
        setClassrooms(res.data.data);
        if (res.data.data.length > 0) {
          setClassroomId(res.data.data[0].id);
        }
      }
    }).catch(e => console.error('Failed to fetch classrooms', e));
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchLearners(searchQuery);
  };

  const handleRegisterLearner = async (e) => {
    e.preventDefault();
    if (!firstName || !lastName || !birthdate || !learnerIdCode || !parentId || !cdcId) {
      alert('Please fill in all required fields.');
      return;
    }

    setRegLoading(true);
    try {
      await api.post('/learners', {
        firstName,
        lastName,
        birthdate: new Date(birthdate).toISOString(),
        gender: Number(gender),
        learnerIdCode,
        parentId,
        cdcId
      });

      // Clear states & close modal
      setFirstName('');
      setLastName('');
      setBirthdate('');
      setGender(0);
      setLearnerIdCode('');
      setShowRegModal(false);

      // Refresh list
      fetchLearners();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error?.message || 'Failed to register learner.');
    } finally {
      setRegLoading(false);
    }
  };

  const handleEnrollLearner = async (e) => {
    e.preventDefault();
    if (!selectedLearner || !classroomId) return;

    setEnrollLoading(true);
    try {
      await api.post(`/learners/${selectedLearner.id}/enroll`, {
        learnerId: selectedLearner.id,
        classroomId
      });

      setShowEnrollModal(false);
      setSelectedLearner(null);
      fetchLearners();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error?.message || 'Failed to enroll learner.');
    } finally {
      setEnrollLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>Learners Directory</h2>
          <p style={{ color: '#64748b', margin: '5px 0 0 0' }}>Search and manage child profiles enrolled in Child Development Centers.</p>
        </div>
        <button
          onClick={() => setShowRegModal(true)}
          style={{
            padding: '10px 15px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          + Add New Learner
        </button>
      </div>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '15px', marginTop: '20px' }}>
        <input
          type="text"
          placeholder="Search by learner name, learner ID code..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            flex: 1,
            padding: '10px',
            border: '1px solid #cbd5e1',
            borderRadius: '4px'
          }}
        />
        <button type="submit" style={{
          padding: '10px 20px',
          backgroundColor: '#0f172a',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          fontWeight: 'bold',
          cursor: 'pointer'
        }}>
          Search
        </button>
      </form>

      {error && (
        <div style={{ padding: '10px', backgroundColor: '#fee2e2', color: '#ef4444', borderRadius: '4px', marginTop: '20px' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ marginTop: '40px', textAlign: 'center', color: '#64748b' }}>Loading roster...</div>
      ) : learners.length === 0 ? (
        <div style={{ marginTop: '40px', padding: '40px', textAlign: 'center', border: '1px dashed #cbd5e1', borderRadius: '8px', color: '#64748b' }}>
          No learners registered yet. Click the button above to add one.
        </div>
      ) : (
        <div style={{ marginTop: '30px', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white', border: '1px solid #cbd5e1' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8fafc', borderBottom: '2px solid #cbd5e1', textAlign: 'left' }}>
                <th style={{ padding: '12px 15px' }}>ID Code (LRN)</th>
                <th style={{ padding: '12px 15px' }}>Full Name</th>
                <th style={{ padding: '12px 15px' }}>Gender</th>
                <th style={{ padding: '12px 15px' }}>Birthdate</th>
                <th style={{ padding: '12px 15px' }}>Parent/Guardian</th>
                <th style={{ padding: '12px 15px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {learners.map((l) => (
                <tr key={l.id} style={{ borderBottom: '1px solid #cbd5e1' }}>
                  <td style={{ padding: '12px 15px', fontWeight: 'bold' }}>{l.learnerIdCode}</td>
                  <td style={{ padding: '12px 15px' }}>{l.fullName}</td>
                  <td style={{ padding: '12px 15px' }}>{l.gender === 'Male' || l.gender === 0 ? 'Male' : 'Female'}</td>
                  <td style={{ padding: '12px 15px' }}>{new Date(l.birthdate).toLocaleDateString()}</td>
                  <td style={{ padding: '12px 15px' }}>{l.parentName}</td>
                  <td style={{ padding: '12px 15px', textAlign: 'right' }}>
                    <button
                      onClick={() => {
                        setSelectedLearner(l);
                        setShowEnrollModal(true);
                      }}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      Enroll in Class
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Registration Modal */}
      {showRegModal && (
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
            <h3 style={{ margin: '0 0 20px 0' }}>Register Learner</h3>
            <form onSubmit={handleRegisterLearner} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>First Name *</label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Last Name *</label>
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    required
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Birthdate *</label>
                  <input
                    type="date"
                    value={birthdate}
                    onChange={(e) => setBirthdate(e.target.value)}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Gender *</label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(Number(e.target.value))}
                    style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    required
                  >
                    <option value={0}>Male</option>
                    <option value={1}>Female</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Learner ID Code (LRN) *</label>
                <input
                  type="text"
                  value={learnerIdCode}
                  onChange={(e) => setLearnerIdCode(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                  placeholder="e.g. 1012345678"
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Link Parent / Guardian *</label>
                <select
                  value={parentId}
                  onChange={(e) => setParentId(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                  required
                >
                  {parents.length === 0 ? (
                    <option value="">No parents registered. Register a parent account first.</option>
                  ) : (
                    parents.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.FullName || p.fullName} ({p.RelationshipToLearner || p.relationshipToLearner})
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Affiliated CDC *</label>
                <select
                  value={cdcId}
                  onChange={(e) => setCdcId(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                  required
                >
                  {cdcs.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowRegModal(false)}
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
                  disabled={regLoading}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    cursor: regLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {regLoading ? 'Registering...' : 'Register'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Enrollment Modal */}
      {showEnrollModal && selectedLearner && (
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
            maxWidth: '400px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            boxSizing: 'border-box'
          }}>
            <h3 style={{ margin: '0 0 10px 0' }}>Enroll Learner</h3>
            <p style={{ fontSize: '14px', color: '#64748b', margin: '0 0 20px 0' }}>
              Select a classroom to enroll <strong>{selectedLearner.fullName}</strong>.
            </p>
            <form onSubmit={handleEnrollLearner} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Available Classrooms *</label>
                <select
                  value={classroomId}
                  onChange={(e) => setClassroomId(e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                  required
                >
                  {classrooms.length === 0 ? (
                    <option value="">No classrooms available. Create a class first.</option>
                  ) : (
                    classrooms.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} ({c.subjectName}) - {c.schedule}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowEnrollModal(false);
                    setSelectedLearner(null);
                  }}
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
                  disabled={enrollLoading}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    cursor: enrollLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {enrollLoading ? 'Enrolling...' : 'Enroll'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default LearnerList;
