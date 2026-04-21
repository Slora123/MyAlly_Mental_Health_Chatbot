// Theme configuration for all four moods

export const THEMES = {
  calm: {
    id: 'calm',
    icon: '🎨',
    name: 'Calm Light',
    avatar: '😊',
    status: 'here for you, always',
  },
  happy: {
    id: 'happy',
    icon: '💗',
    name: 'Soft Pink',
    avatar: '🥰',
    status: 'feeling joyful with you ✨',
  },
  angry: {
    id: 'angry',
    icon: '🔥',
    name: 'Bad Mood',
    avatar: '🥺',
    status: "I'm here through the storm 🌩️",
  },
  night: {
    id: 'night',
    icon: '🌙',
    name: 'Dark Night',
    avatar: '😴',
    status: 'with you through the night 🌙',
  },
};

// Mood detection rules (client-side, instant)
export const MOOD_RULES = [
  {
    theme: 'angry',
    keywords: [
      'angry', 'anger', 'hate', 'frustrated', 'irritated', 'furious',
      'worst', 'horrible', 'everything is wrong', 'so mad', 'pissed',
      'annoyed', 'rage', 'so angry', 'gussa', 'bahut gussa',
    ],
  },
  {
    theme: 'happy',
    keywords: [
      'happy', 'joyful', 'amazing', 'great', 'fantastic', 'so happy',
      'passed', 'won', 'excited', 'yay', 'celebrate', 'love it',
      'wonderful', 'thrilled', 'khush', 'mast', 'badiya', 'awesome',
      'flying colors',
    ],
  },
  {
    theme: 'night',
    keywords: [
      'lonely', "can't sleep", 'can not sleep', 'late night', 'night',
      'wandering', 'overthinking', 'hopeless', 'numb', 'lost', 'emptiness',
      'midnight', '2am', '3am', 'raat', 'neend nahi', 'what if thoughts',
      'sad', 'depressed', 'depression',
    ],
  },
];

export function detectThemeFromText(text) {
  const lower = text.toLowerCase();
  for (const rule of MOOD_RULES) {
    if (rule.keywords.some((kw) => lower.includes(kw))) {
      return rule.theme;
    }
  }
  return null;
}
