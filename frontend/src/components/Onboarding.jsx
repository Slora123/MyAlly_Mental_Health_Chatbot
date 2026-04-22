import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Onboarding({ authToken }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nickname: '',
    gender: '',
    preferred_tone: 'Casual',
    support_style: 'Listening',
    lifestyle_patterns: '',
    support_network: '',
    education: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/user/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        navigate('/chat');
      }
    } catch (err) {
      console.error(err);
      alert('Failed to save profile');
    }
  };

  return (
    <div className="reg-container" style={{ alignItems: 'flex-start', paddingTop: '50px', overflowY: 'auto' }}>
      <div className="reg-card glass" style={{ width: '100%', maxWidth: '600px' }}>
        <h1 className="reg-title">Let's Personalize Your Experience</h1>
        <p className="reg-subtitle">Help MyAlly understand you better so we can provide the best support.</p>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '20px' }}>
          <div className="reg-input-group">
            <label className="reg-label">What should I call you? (Name or Nickname)</label>
            <input type="text" name="nickname" className="reg-input" value={formData.nickname} onChange={handleChange} required />
          </div>

          <div className="reg-input-group">
            <label className="reg-label">Gender</label>
            <select name="gender" className="reg-input" value={formData.gender} onChange={handleChange} required>
              <option value="">Select...</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Non-binary">Non-binary</option>
              <option value="Prefer not to say">Prefer not to say</option>
            </select>
          </div>

          <div className="reg-input-group">
            <label className="reg-label">Preferred Tone</label>
            <select name="preferred_tone" className="reg-input" value={formData.preferred_tone} onChange={handleChange}>
              <option value="Casual">Casual / Chill</option>
              <option value="Formal">Formal / Professional</option>
              <option value="Humorous">Humorous / Lighthearted</option>
              <option value="Direct">Direct / Straightforward</option>
            </select>
          </div>

          <div className="reg-input-group">
            <label className="reg-label">How do you usually like to be supported?</label>
            <select name="support_style" className="reg-input" value={formData.support_style} onChange={handleChange}>
              <option value="Listening">Just listen and validate me</option>
              <option value="Advice">Give me actionable advice</option>
              <option value="Distraction">Distract me with lighter topics</option>
              <option value="Motivation">Motivate and encourage me</option>
            </select>
          </div>

          <div className="reg-input-group">
            <label className="reg-label">Sleep or routine patterns (e.g., "Night owl", "Struggle to sleep")</label>
            <input type="text" name="lifestyle_patterns" className="reg-input" value={formData.lifestyle_patterns} onChange={handleChange} />
          </div>

          <div className="reg-input-group">
            <label className="reg-label">Who do you usually talk to? (Friends, family, no one)</label>
            <input type="text" name="support_network" className="reg-input" value={formData.support_network} onChange={handleChange} />
          </div>

          <div className="reg-input-group">
            <label className="reg-label">Education / Current Academic Level</label>
            <input type="text" name="education" className="reg-input" value={formData.education} onChange={handleChange} />
          </div>

          <button type="submit" className="reg-btn" style={{ marginTop: '20px' }}>Save & Continue</button>
        </form>
      </div>
    </div>
  );
}
