import { THEMES } from '../themes';
import styles from './MessageBubble.module.css';

function timeStr(iso) {
  return new Date(iso).toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

export default function MessageBubble({ item, theme, hideAvatar, animate }) {
  const isUser = item.role === 'user';
  const t = THEMES[theme];
  const avatar = isUser ? '🧑‍🎓' : t.avatar;

  return (
    <div
      className={`${styles.row} ${isUser ? styles.user : styles.bot} ${hideAvatar ? styles.hideAvatar : ''}`}
      style={animate ? { animation: 'msg-in 0.38s cubic-bezier(0.175,0.885,0.32,1.2) both' } : { animation: 'none' }}
    >
      <div className={styles.avatarWrap} aria-hidden="true">
        <div className={`${styles.avatar} ${isUser ? styles.avatarUser : styles.avatarBot}`}>
          {avatar}
        </div>
      </div>

      <div className={`${styles.content} ${isUser ? styles.contentUser : styles.contentBot}`}>
        <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleBot}`}>
          {item.text}
        </div>
        <time className={`${styles.time} ${isUser ? styles.timeUser : styles.timeBot}`}>
          {timeStr(item.time)}
        </time>
      </div>
    </div>
  );
}
