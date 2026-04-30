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
import './App.css';

export default function App() {
  const [authToken, setAuthTokenState] = useState(localStorage.getItem('myally_token'));
  const isAdmin = window.location.pathname === '/admin';

  const setAuthToken = (token) => {
    if (token) {
      localStorage.setItem('myally_token', token);
    } else {
      localStorage.removeItem('myally_token');
    }
    setAuthTokenState(token);
  };

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

function ChatApp({ authToken, setAuthToken }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [theme, setTheme] = useState('calm');
  const [sessionId, setSessionId] = useState(null);

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
      const fetchInitialSession = async () => {
        try {
          const res = await fetch('/api/chats', {
            headers: { 'Authorization': `Bearer ${authToken}` }
          });
          if (res.status === 401) {
            setAuthToken(null);
            return;
          }
          if (res.ok) {
            const data = await res.json();
            if (data.sessions && data.sessions.length > 0) {
              setSessionId(data.sessions[0].id);
            }
          }
        } catch (err) {
          console.error('Failed to load initial session:', err);
        }
      };
      fetchInitialSession();
    }
  }, [authToken]);

  // Load chat history when session changes
  useEffect(() => {
    if (sessionId) {
      fetchHistory(sessionId);
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  const fetchHistory = async (id) => {
    try {
      const res = await fetch(`/api/chats/${id}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        // convert to format used by UI
        const loadedMessages = data.messages.map(m => ({
          role: m.role,
          text: m.content,
          time: m.created_at
        }));
        setMessages(loadedMessages);
      }
    } catch (err) {
      console.error(err);
    }
  };

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

  return (
    <div className="app-wrapper">
      <div className="chat-glass-card">
        <Header theme={theme} onSetTheme={setTheme} />
        <main className="chat-container" ref={chatContainerRef}>
          {messages.length === 0 && (
            <WelcomeBanner onChipClick={(text) => handleSendMessage(text)} />
          )}
          {messages.map((msg, i) => (
            <MessageBubble key={i} item={msg} theme={theme} animate={i === messages.length - 1} />
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
  );
}
