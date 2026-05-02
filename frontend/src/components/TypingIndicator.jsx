import { THEMES } from '../themes';
import styles from './TypingIndicator.module.css';

export default function TypingIndicator({ theme }) {
  const t = THEMES[theme];

  return (
    <div className={styles.row} aria-live="polite" aria-label="MyAlly is typing">
      <div className={`${styles.avatar} glass`} aria-hidden="true">
        {t.avatar}
      </div>
      <div className={styles.bubble}>
        <span className={styles.dot} />
        <span className={styles.dot} />
        <span className={styles.dot} />
      </div>
    </div>
  );
}
