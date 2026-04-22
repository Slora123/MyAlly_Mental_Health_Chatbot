import React, { useEffect, useState } from 'react';
import './Sidebar.css';

export default function Sidebar({ authToken, currentSessionId, onSelectSession, onNewChat }) {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    if (authToken) {
      fetchSessions();
    }
  }, [authToken, currentSessionId]); // re-fetch when a new session might be created

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
      console.error('Failed to fetch sessions', err);
    }
  };

  return (
    <div className="sidebar glass">
      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>
      <div className="session-list">
        {sessions.map(session => (
          <div 
            key={session.id} 
            className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            <div className="session-icon">💬</div>
            <div className="session-title">{session.title}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
