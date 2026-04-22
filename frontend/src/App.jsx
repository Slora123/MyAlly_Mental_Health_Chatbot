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
  const [authToken, setAuthToken] = useState(null);
  const isAdmin = window.location.pathname === '/admin';

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
        authToken ? <ChatApp authToken={authToken} /> : <Navigate to="/" />
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

function ChatApp({ authToken }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [theme, setTheme] = useState('calm');
  const [sessionId, setSessionId] = useState(null);
  
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  useEffect(() => {
    document.body.className = `theme-${theme}`;
  }, [theme]);

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
    <div className="app-wrapper" style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      padding: '20px' 
    }}>
      <div className="chat-glass-card" style={{ 
        width: '100%', 
        maxWidth: '1200px', 
        height: '92vh',
        background: 'rgba(255, 250, 245, 0.85)',
        backdropFilter: 'blur(30px)',
        WebkitBackdropFilter: 'blur(30px)',
        borderRadius: '32px',
        border: '1px solid rgba(255, 255, 255, 0.5)',
        boxShadow: '0 40px 100px -20px rgba(0, 0, 0, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        position: 'relative'
      }}>
        <Header theme={theme} onSetTheme={setTheme} />
        <main className="chat-container">
          {messages.length === 0 && (
            <WelcomeBanner onChipClick={(text) => handleSendMessage(text)} />
          )}
          {messages.map((msg, i) => (
            <MessageBubble key={i} item={msg} theme={theme} animate={i === messages.length - 1} />
          ))}
          {isTyping && <TypingIndicator theme={theme} />}
          <div ref={chatEndRef} />
        </main>
        <footer className="input-area">
          <div className="input-pill">
            <input
              type="text"
              className="chat-input"
              placeholder="Type your message here..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <button className="send-btn" onClick={() => handleSendMessage()} disabled={!inputText.trim() || isTyping}>
              <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" /></svg>
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
