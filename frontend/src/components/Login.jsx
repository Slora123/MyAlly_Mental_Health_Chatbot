import React from 'react';
import { signInWithPopup } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { useNavigate } from 'react-router-dom';

export default function Login({ setAuthToken }) {
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      setAuthToken(token);
      checkProfile(token);
    } catch (error) {
      console.error("Login failed", error);
      alert("Login failed: " + error.message);
    }
  };

  const handleDevLogin = () => {
    // Bypass for local development if Firebase isn't configured yet
    const token = "dummy-dev-token";
    setAuthToken(token);
    checkProfile(token);
  };

  const checkProfile = async (token) => {
    try {
      const res = await fetch('/api/user/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const user = await res.json();
        // If nickname is null, they haven't completed onboarding
        if (!user.nickname && !user.gender) {
          navigate('/onboarding');
        } else {
          navigate('/chat');
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="reg-container">
      <div className="reg-card glass" style={{ textAlign: 'center' }}>
        <h1 className="reg-title">Welcome to MyAlly 👋</h1>
        <p className="reg-subtitle">Sign in to start your personalized mental wellness journey.</p>
        
        <button className="reg-btn" onClick={handleGoogleLogin} style={{ marginTop: '20px', background: '#fff', color: '#333' }}>
          <img src="https://img.icons8.com/color/24/000000/google-logo.png" alt="Google" style={{ verticalAlign: 'middle', marginRight: '10px' }}/>
          Continue with Google
        </button>

        <p style={{ marginTop: '20px', fontSize: '0.8rem', opacity: 0.6 }}>
          or for local testing:
        </p>
        <button className="reg-btn" onClick={handleDevLogin} style={{ background: '#444', marginTop: '10px' }}>
          Developer Bypass
        </button>
      </div>
    </div>
  );
}
