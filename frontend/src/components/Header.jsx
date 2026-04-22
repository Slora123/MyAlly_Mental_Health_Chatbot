import { useState, useRef, useEffect } from 'react';
import { THEMES } from '../themes';
import styles from './Header.module.css';

export default function Header({ theme, onSetTheme }) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);
  const t = THEMES[theme];

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <header className={styles.header}>
      {/* Left — Branding/Profile */}
      <div className={styles.profile}>
        <div className={styles.avatar} aria-label="MyAlly avatar">
          {t.avatar}
        </div>
        <div className={styles.info}>
          <h2 className={styles.name}>MyAlly</h2>
          <p className={styles.status}>
            <span className={styles.onlineDot} aria-hidden="true" />
            <span id="header-status">{t.status}</span>
          </p>
        </div>
      </div>

      {/* Right — theme picker */}
      <div className={styles.pickerWrap} ref={dropdownRef}>
        <button
          className={styles.themeBtn}
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          aria-label="Change theme"
        >
          <span>{t.icon}</span>
          <span className={styles.themeName}>{t.name}</span>
          <span className={`${styles.chevron} ${open ? styles.chevronOpen : ''}`}>▾</span>
        </button>

        {open && (
          <div className={`${styles.dropdown} glass`} role="listbox">
            {Object.values(THEMES).map((th) => (
              <button
                key={th.id}
                className={`${styles.themeOption} ${theme === th.id ? styles.active : ''}`}
                role="option"
                aria-selected={theme === th.id}
                onClick={() => {
                  onSetTheme(th.id);
                  setOpen(false);
                }}
              >
                <span>{th.icon}</span>
                <span>{th.name}</span>
                {theme === th.id && <span className={styles.checkMark}>✓</span>}
              </button>
            ))}
          </div>
        )}
      </div>
    </header>
  );
}
