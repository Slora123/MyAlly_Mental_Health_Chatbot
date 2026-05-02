import { useState, useEffect, useRef } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import Header from './components/Header';
import MessageBubble from './components/MessageBubble';
import WelcomeBanner from './components/WelcomeBanner';
import TypingIndicator from './components/TypingIndicator';
import Sidebar from './components/Sidebar';
import Login from './components/Login';
import Onboarding from './components/Onboarding';
import CounselorDashboard from './CounselorDashboard';
import { detectThemeFromText } from './themes';
import { auth } from './firebase';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { botDefault, botFemale, botMale } from './assets/avatars.js';
import './App.css';

export default function App() {
  // Use sessionStorage so each browser tab has its own independent auth state.
  // Closing a tab or opening a new tab always starts fresh at the login page.
  const [authToken, setAuthTokenState] = useState(sessionStorage.getItem('myally_token'));
  const [loading, setLoading] = useState(true);
  const isAdmin = window.location.pathname === '/admin';

  const setAuthToken = (token) => {
    if (token) {
      sessionStorage.setItem('myally_token', token);
      // Also keep in localStorage for cross-tab token refresh (backend calls)
      localStorage.setItem('myally_token', token);
    } else {
      sessionStorage.removeItem('myally_token');
      localStorage.removeItem('myally_token');
    }
    setAuthTokenState(token);
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        console.log("👤 [App] Auth state changed: User is logged in", user.email);
        const token = await user.getIdToken();
        
        // Update tokens
        sessionStorage.setItem('myally_token', token);
        localStorage.setItem('myally_token', token);
        setAuthTokenState(token);

        // Check if we need to navigate (only if we are on the login page)
        if (window.location.pathname === '/') {
          try {
            const res = await fetch('/api/user/profile', {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
              const profile = await res.json();
              if (profile && profile.nickname) {
                console.log("✅ [App] Profile found. Navigating to chat.");
                navigate('/chat');
              } else {
                console.log("⚠️ [App] No nickname found. Navigating to onboarding.");
                navigate('/onboarding');
              }
            } else {
              navigate('/chat');
            }
          } catch (err) {
            console.warn("Profile check failed during silent refresh:", err);
            navigate('/chat');
          }
        }
      } else {
        console.log("👤 [App] No Firebase user. Clearing all tokens.");
        sessionStorage.removeItem('myally_token');
        localStorage.removeItem('myally_token');
        setAuthTokenState(null);
        if (window.location.pathname !== '/') {
          navigate('/');
        }
      }
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);


  if (loading) {
    return (
      <div style={{
        height: '100vh', display: 'flex', flexDirection: 'column', 
        justifyContent: 'center', alignItems: 'center', 
        background: 'linear-gradient(135deg, #f3e8ff 0%, #fce7f3 50%, #fff1f1 100%)',
        fontFamily: "'Outfit', sans-serif"
      }}>
        <div className="loader"></div>
        <h2 style={{ marginTop: '20px', color: '#1e293b' }}>Initializing MyAlly...</h2>
      </div>
    );
  }

  if (isAdmin) {
    return <CounselorDashboard />;
  }

  return (
    <Routes>
      <Route path="/" element={<Login setAuthToken={setAuthToken} />} />
      <Route path="/onboarding" element={
        authToken ? <Onboarding authToken={authToken} /> : <Navigate to="/" />
      } />
      <Route path="/chat" element={
        authToken ? <ChatApp authToken={authToken} setAuthToken={setAuthToken} /> : <Navigate to="/" />
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

async function handleLogout(setAuthToken) {
  try {
    await signOut(auth);
  } catch (e) {
    console.warn('Sign out error:', e);
  }
  sessionStorage.removeItem('myally_token');
  localStorage.removeItem('myally_token');
  setAuthToken(null);
  window.location.href = '/';
}

function ChatApp({ authToken, setAuthToken }) {

  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [theme, setTheme] = useState('calm');
  const [sessionId, setSessionId] = useState(null);
  const [userEmail, setUserEmail] = useState('');
  const [userProfile, setUserProfile] = useState(null);
  
  // Avatar states
  const [myAllyAvatar, setMyAllyAvatar] = useState(null);
  const [userAvatar, setUserAvatar] = useState(null);

  const chatContainerRef = useRef(null);


  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Set body theme class on change
  useEffect(() => {
    document.body.className = `theme-${theme}`;
  }, [theme]);

  // Set initial theme class synchronously so CSS vars load right away
  if (typeof document !== 'undefined' && !document.body.className) {
    document.body.className = 'theme-calm';
  }

  // Load initial session on mount
  useEffect(() => {
    if (authToken) {
      // Fetch user profile to get email
      fetch('/api/user/profile', {
        headers: { 'Authorization': `Bearer ${authToken}` }
      }).then(r => r.ok ? r.json() : null)
        .then(profile => { 
          if (profile) {
            if (profile.email) setUserEmail(profile.email); 
            if (profile.avatar_url) setUserAvatar(profile.avatar_url);
            if (profile.bot_avatar_url) setMyAllyAvatar(profile.bot_avatar_url);
            setUserProfile(profile);
          }
        })
        .catch(() => {});

      const fetchAllHistory = async () => {
        try {
          const res = await fetch('/api/chats/all', {
            headers: { 'Authorization': `Bearer ${authToken}` }
          });
          if (res.status === 401) {
            setAuthToken(null);
            return;
          }
          if (res.ok) {
            const data = await res.json();
            if (data.session_id) {
              setSessionId(data.session_id);
            }
            if (data.messages) {
              const loadedMessages = data.messages.map(m => ({
                role: m.role,
                text: m.content,
                time: m.created_at
              }));
              setMessages(loadedMessages);
            }
          }
        } catch (err) {
          console.error('Failed to load chat history:', err);
        }
      };
      fetchAllHistory();
    }
  }, [authToken]);

  const handleSendMessage = async (textOverride) => {
    const text = textOverride || inputText;
    if (!text.trim() || isTyping) return;

    const userMsg = { role: 'user', text: text, time: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    const detected = detectThemeFromText(text);
    if (detected) setTheme(detected);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (response.status === 401) {
        console.error('Session expired, logging out...');
        setAuthToken(null);
        return;
      }

      const data = await response.json();
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
      }

      const botMsg = {
        role: 'bot',
        text: data.reply || "I'm sorry, I encountered an error. Please try again.",
        time: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('Chat error:', err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSaveProfile = async (updates) => {
    if (!authToken) return;
    try {
      const res = await fetch('/api/user/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(updates),
      });
      if (res.ok) {
        const data = await res.json();
        setUserProfile(data.user);
      }
    } catch (err) {
      console.error('Failed to save profile:', err);
    }
  };

  return (
    <div className="app-wrapper">
      <div className="chat-glass-card" style={{ 
        position: 'relative', 
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column'
      }}>
        
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0, position: 'relative' }}>
          
          <Header
            theme={theme}
            onSetTheme={setTheme}
            userEmail={userEmail}
            authToken={authToken}
            onLogout={() => handleLogout(setAuthToken)}
            userProfile={userProfile}
            myAllyAvatar={myAllyAvatar}
            setMyAllyAvatar={(url) => { setMyAllyAvatar(url); handleSaveProfile({ bot_avatar_url: url }); }}
            userAvatar={userAvatar}
            setUserAvatar={(url) => { setUserAvatar(url); handleSaveProfile({ avatar_url: url }); }}
          />
          <main className="chat-container" ref={chatContainerRef}>
            {messages.length === 0 && (
              <WelcomeBanner onChipClick={(text) => handleSendMessage(text)} />
            )}
            {messages.map((msg, i) => (
              <MessageBubble 
                key={i} 
                item={msg} 
                theme={theme} 
                animate={i === messages.length - 1} 
                botImg={myAllyAvatar || (userProfile?.gender?.toLowerCase() === 'female' ? botFemale : (userProfile?.gender?.toLowerCase() === 'male' ? botMale : botDefault))}
                userAvatar={userAvatar}
              />
            ))}
            {isTyping && <TypingIndicator theme={theme} />}
          </main>
          <footer className="input-area">
            <div className="input-pill">
              <span className="input-icon">😊</span>
              <input
                type="text"
                id="chat-text-input"
                className="chat-input"
                placeholder="Type how you feel..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <button id="send-message-btn" className="send-btn" onClick={() => handleSendMessage()} disabled={!inputText.trim() || isTyping}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
