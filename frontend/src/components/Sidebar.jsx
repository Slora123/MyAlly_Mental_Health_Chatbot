import { useState, useEffect } from 'react';
import './Sidebar.css';

export default function Sidebar({ authToken, currentSessionId, onSelectSession, onNewChat }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authToken) {
      fetchSessions();
    }
  }, [authToken]);

  const fetchSessions = async () => {
    try {
      const res = await fetch('/api/chats', {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sidebar">
      <button className="new-chat-btn" onClick={onNewChat}>
        <span style={{ marginRight: '10px' }}>+</span> New Chat
      </button>
      
      <div className="session-list">
        {loading ? (
          <p style={{ color: 'rgba(255,255,255,0.5)', padding: '0 10px' }}>Loading history...</p>
        ) : sessions.length === 0 ? (
          <p style={{ color: 'rgba(255,255,255,0.4)', padding: '0 10px', fontSize: '0.85rem' }}>No recent chats</p>
        ) : (
          sessions.map((session) => (
            <div 
              key={session.id} 
              className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
              onClick={() => onSelectSession(session.id)}
            >
              <span className="session-icon">💬</span>
              <span className="session-title">{session.title || 'Untitled Chat'}</span>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer" style={{ marginTop: 'auto', padding: '10px 0', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
        <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.75rem', textAlign: 'center' }}>
          MyAlly v1.0
        </div>
      </div>
    </div>
  );
}
