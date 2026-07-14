import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../../lib/api';

export const Register = () => {
  const [cdcs, setCdcs] = useState([]);
  const [role, setRole] = useState('Teacher');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Common Form States
  const [userName, setUserName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [mobile, setMobile] = useState('');
  const [address, setAddress] = useState('');
  const [consent, setConsent] = useState(false);

  // Teacher Form States
  const [employeeId, setEmployeeId] = useState('');
  const [position, setPosition] = useState('');
  const [cdcId, setCdcId] = useState('');

  // Parent Form States
  const [relationship, setRelationship] = useState('');

  const navigate = useNavigate();

  // Load CDCs on mount
  useEffect(() => {
    const fetchCdcs = async () => {
      try {
        const response = await api.get('/cdc');
        if (response.data?.data) {
          setCdcs(response.data.data);
          if (response.data.data.length > 0) {
            setCdcId(response.data.data[0].id);
          }
        }
      } catch (err) {
        console.error('Failed to load CDCs', err);
      }
    };
    fetchCdcs();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!userName || !email || !password || !fullName) {
      setError('Please fill in all required fields.');
      return;
    }

    if (!consent) {
      setError('You must consent to the Data Processing agreement (DPA) to register.');
      return;
    }

    setLoading(true);

    try {
      if (role === 'Teacher') {
        if (!employeeId || !position || !cdcId) {
          setError('Please fill in all teacher specific details.');
          setLoading(false);
          return;
        }

        await api.post('/auth/register/teacher', {
          userName,
          email,
          password,
          fullName,
          employeeId,
          position,
          mobile,
          address,
          cdcId,
          consentedToToS: consent
        });
      } else {
        if (!relationship) {
          setError('Please specify your relationship to the learner.');
          setLoading(false);
          return;
        }

        await api.post('/auth/register/parent', {
          userName,
          email,
          password,
          fullName,
          relationshipToLearner: relationship,
          mobile,
          address,
          consentedToToS: consent
        });
      }

      setSuccess('Registration successful! Redirecting to login page...');
      setTimeout(() => {
        navigate('/login');
      }, 2500);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.error?.message || 
        'Registration failed. Username or email might be taken.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: '#f1f5f9',
      fontFamily: 'sans-serif',
      padding: '20px 0'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '500px'
      }}>
        <h2 style={{ textAlign: 'center', margin: '0 0 10px 0', color: '#0f172a' }}>Create Account</h2>
        <p style={{ textAlign: 'center', color: '#64748b', fontSize: '14px', margin: '0 0 30px 0' }}>
          ECCD Monitoring System Registration
        </p>

        {/* Role Tab Selector */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '25px' }}>
          <button
            type="button"
            onClick={() => setRole('Teacher')}
            style={{
              flex: 1,
              padding: '10px',
              backgroundColor: role === 'Teacher' ? '#3b82f6' : '#e2e8f0',
              color: role === 'Teacher' ? 'white' : '#0f172a',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            Teacher / Admin
          </button>
          <button
            type="button"
            onClick={() => setRole('Parent')}
            style={{
              flex: 1,
              padding: '10px',
              backgroundColor: role === 'Parent' ? '#3b82f6' : '#e2e8f0',
              color: role === 'Parent' ? 'white' : '#0f172a',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            Parent
          </button>
        </div>

        {error && (
          <div style={{ padding: '10px', backgroundColor: '#fee2e2', color: '#ef4444', borderRadius: '4px', marginBottom: '20px', fontSize: '14px' }}>
            {error}
          </div>
        )}

        {success && (
          <div style={{ padding: '10px', backgroundColor: '#dcfce7', color: '#15803d', borderRadius: '4px', marginBottom: '20px', fontSize: '14px' }}>
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {/* Common fields */}
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Full Name *</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
              placeholder="e.g. Maria Clara"
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Username *</label>
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                placeholder="mariaclara"
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Email Address *</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                placeholder="maria@email.com"
                required
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Password *</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                placeholder="Min 8 chars"
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Mobile Number</label>
              <input
                type="text"
                value={mobile}
                onChange={(e) => setMobile(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                placeholder="0917xxxxxxx"
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Home Address</label>
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
              placeholder="St., Barangay, City"
            />
          </div>

          {/* Teacher fields */}
          {role === 'Teacher' && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Employee ID *</label>
                  <input
                    type="text"
                    value={employeeId}
                    onChange={(e) => setEmployeeId(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    placeholder="EMP-123"
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Position *</label>
                  <input
                    type="text"
                    value={position}
                    onChange={(e) => setPosition(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                    placeholder="e.g. Teacher I"
                    required
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Affiliated CDC *</label>
                <select
                  value={cdcId}
                  onChange={(e) => setCdcId(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                  required
                >
                  {cdcs.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            </>
          )}

          {/* Parent fields */}
          {role === 'Parent' && (
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: 'bold' }}>Relationship to Learner *</label>
              <input
                type="text"
                value={relationship}
                onChange={(e) => setRelationship(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '4px', boxSizing: 'border-box' }}
                placeholder="e.g. Mother, Father, Guardian"
                required
              />
            </div>
          )}

          {/* Consent / ToS */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', marginTop: '10px' }}>
            <input
              type="checkbox"
              id="consent"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              style={{ marginTop: '3px' }}
            />
            <label htmlFor="consent" style={{ fontSize: '12px', color: '#475569', lineHeight: 1.4 }}>
              I consent to the collection and processing of personal information under the Philippine Data Privacy Act of 2012 (RA 10173).
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '10px',
              backgroundColor: loading ? '#93c5fd' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 'bold',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginTop: '10px'
            }}
          >
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <div style={{ marginTop: '25px', textAlign: 'center', fontSize: '14px' }}>
          <span style={{ color: '#64748b' }}>Already have an account? </span>
          <Link to="/login" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: 'bold' }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
export default Register;
