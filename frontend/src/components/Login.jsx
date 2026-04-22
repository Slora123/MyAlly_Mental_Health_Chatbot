import React, { useState } from 'react';
import { signInWithPopup } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { useNavigate } from 'react-router-dom';

export default function Login({ setAuthToken }) {
  const navigate = useNavigate();
  const [role, setRole] = useState(null); // 'user' or 'admin'

  const handleGoogleLogin = async (mode) => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      setAuthToken(token);

      if (role === 'admin') {
        window.location.href = '/admin';
      } else {
        checkProfile(token, mode);
      }
    } catch (error) {
      console.error("Login failed", error);
      alert("Login failed: " + error.message);
    }
  };

  const checkProfile = async (token, mode) => {
    try {
      const res = await fetch('/api/user/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        if (mode === 'create') {
          navigate('/onboarding');
        } else {
          // Sign In mode — go straight to chat
          navigate('/chat');
        }
      } else {
        const errData = await res.json();
        alert("Authentication failed: " + (errData.detail || "Unknown error"));
      }
    } catch (err) {
      console.error(err);
      alert("Backend connection error: " + err.message);
    }
  };

  if (!role) {
    return (
      <div className="login-wrapper" style={{
        background: 'linear-gradient(135deg, #f3e8ff 0%, #fce7f3 50%, #fff1f1 100%)',
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: "'Outfit', sans-serif",
        overflow: 'hidden'
      }}>
        <div style={{
          display: 'flex',
          width: '92%',
          maxWidth: '1200px',
          height: '80vh',
          borderRadius: '48px',
          overflow: 'hidden',
          background: 'rgba(255, 250, 245, 0.85)', // Soft tinted card
          backdropFilter: 'blur(30px)',
          WebkitBackdropFilter: 'blur(30px)',
          border: '1px solid rgba(255, 255, 255, 0.5)',
          boxShadow: '0 40px 100px -20px rgba(253, 29, 29, 0.05)',
          position: 'relative'
        }}>
          {/* Left Side: Content */}
          <div style={{ flex: 1, padding: '70px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <h1 style={{
              fontSize: '4.8rem',
              fontWeight: '900',
              color: '#1e293b',
              marginBottom: '10px',
              letterSpacing: '-2px',
              lineHeight: 1
            }}>
              Welcome to <br />
              <span style={{
                background: 'linear-gradient(to right, #833ab4, #fd1d1d, #fcb045)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block'
              }}>
                MyAlly
              </span>
            </h1>
            <p style={{ color: '#64748b', fontSize: '1.3rem', marginBottom: '50px', fontWeight: '400' }}>
              Your dedicated space for mental wellness and support.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div
                className="role-option"
                onClick={() => setRole('student')}
                style={{
                  background: 'rgba(255, 255, 255, 0.5)',
                  padding: '40px 30px',
                  borderRadius: '28px',
                  cursor: 'pointer',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  border: '1px solid rgba(0,0,0,0.03)',
                  textAlign: 'left',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px'
                }}
              >
                <div style={{ color: '#fd1d1d' }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                </div>
                <div>
                  <h2 style={{ color: '#1e293b', fontSize: '1.6rem', fontWeight: '700', marginBottom: '4px' }}>Student</h2>
                  <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>Personalized support</p>
                </div>
              </div>

              <div
                className="role-option"
                onClick={() => setRole('admin')}
                style={{
                  background: 'rgba(255, 255, 255, 0.5)',
                  padding: '40px 30px',
                  borderRadius: '28px',
                  cursor: 'pointer',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  border: '1px solid rgba(0,0,0,0.03)',
                  textAlign: 'left',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px'
                }}
              >
                <div style={{ color: '#833ab4' }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>
                </div>
                <div>
                  <h2 style={{ color: '#1e293b', fontSize: '1.6rem', fontWeight: '700', marginBottom: '4px' }}>Counselor</h2>
                  <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>Guardian panel</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side: Image Mockup */}
          <div style={{
            flex: 1,
            background: 'url(/login-mockup.png)',
            backgroundSize: '100% 100%',
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center',
            position: 'relative',
            borderRadius: '0 48px 48px 0',
            backgroundColor: 'transparent'
          }}>
          </div>
        </div>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&display=swap');
          .role-option:hover {
            transform: translateY(-5px);
            background: white !important;
            border-color: #fd1d1d !important;
            box-shadow: 0 15px 30px rgba(253, 29, 29, 0.08);
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="login-wrapper" style={{
      background: 'linear-gradient(135deg, #f3e8ff 0%, #fce7f3 50%, #ffedd5 100%)',
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      fontFamily: "'Outfit', sans-serif"
    }}>
      <div className="auth-card" style={{
        width: '100%',
        maxWidth: '450px',
        padding: '60px 40px',
        borderRadius: '40px',
        background: 'rgba(255, 250, 245, 0.98)',
        textAlign: 'center',
        position: 'relative',
        boxShadow: '0 30px 60px -12px rgba(0,0,0,0.1)',
        animation: 'slideUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1)',
        border: '1px solid rgba(255, 255, 255, 0.5)'
      }}>
        <button
          onClick={() => setRole(null)}
          style={{
            background: 'rgba(0,0,0,0.03)', border: 'none', color: '#64748b', cursor: 'pointer',
            position: 'absolute', top: '30px', left: '30px', fontSize: '1.2rem',
            width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: '0.3s'
          }}
          className="back-btn"
        >
          ←
        </button>

        <h1 style={{ color: '#1e293b', fontSize: '2.5rem', fontWeight: '900', marginBottom: '10px' }}>
          {role === 'admin' ? 'Counselor' : 'Student'}
        </h1>
        <p style={{ color: '#64748b', fontSize: '1.1rem', marginBottom: '40px' }}>
          Secure access to your portal
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <button
            className="auth-btn"
            onClick={() => handleGoogleLogin('signin')}
            style={{
              background: 'linear-gradient(to right, #833ab4, #fd1d1d, #fcb045)',
              color: 'white',
              fontWeight: '800',
              padding: '18px',
              border: 'none',
              borderRadius: '16px',
              cursor: 'pointer',
              fontSize: '1.1rem',
              transition: '0.3s',
              boxShadow: '0 10px 20px rgba(253, 29, 29, 0.2)'
            }}
          >
            {role === 'student' ? 'Sign In with Google' : 'Continue with Google'}
          </button>

          <button
            className="create-btn"
            onClick={() => handleGoogleLogin('create')}
            style={{
              background: 'rgba(0,0,0,0.03)',
              color: '#1e293b',
              fontWeight: '700',
              padding: '16px',
              border: '1px solid rgba(0,0,0,0.05)',
              borderRadius: '16px',
              cursor: 'pointer',
              fontSize: '1rem',
              transition: '0.3s'
            }}
          >
            Create Account
          </button>

          <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginTop: '15px' }}>
            By continuing, you agree to our Terms of Service.
          </p>
        </div>
      </div>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&display=swap');
        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .back-btn:hover { background: #f1f5f9; color: #1e293b; transform: scale(1.1); }
        .auth-btn:hover { transform: translateY(-3px); box-shadow: 0 15px 30px rgba(253, 29, 29, 0.4); }
        .create-btn:hover { background: rgba(0,0,0,0.06); transform: translateY(-2px); }
      `}</style>
    </div>
  );
}
