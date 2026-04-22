# MyAlly: A Premium AI Mental-Health Companion 🛡️✨

**MyAlly** is a state-of-the-art, empathy-aware mental health support chatbot designed specifically for students. It combines **Retrieval-Augmented Generation (RAG)** with a personalized memory layer and a robust crisis escalation protocol to provide a safe, supportive, and human-like experience.

---

## 🌟 Key Features

### 1. 🧠 Personalized Empathy & Memory
- **Onboarding Flow:** Collects user preferences (tone, gender, support style, lifestyle) during the first login to tailor the AI's persona.
- **PostgreSQL Persistence:** All chat sessions and user profiles are stored in a database (SQLAlchemy + Postgres), ensuring long-term memory across devices.
- **Contextual RAG:** Uses dual Chroma collections (`empathy` and `knowledge`) to ground responses in verified mental health data and high-empathy dialogue patterns.

### 2. 🛡️ Crisis Guardian Protocol
- **AI Safety Layer:** Uses a specialized safety pipeline to detect high-risk or unstable user messages.
- **Counselor Dashboard:** Automatically escalates genuine crises to an internal **Guardian Panel** (`/admin`) with a full situation summary and chat history.
- **Immediate Support:** Provides instant crisis resources and helpline options to users in distress.

### 3. 💎 Premium Glassmorphism UI
- **Modern Design:** A responsive, dark-mode interface with smooth animations and interactive mood-based theme switching.
- **Chat Sidebar:** A persistent sidebar for managing multiple chat sessions, similar to top-tier AI applications.
- **Firebase Auth:** Secure Google Sign-In integration for a seamless user experience.

---

## 🛠️ Technology Stack

- **Backend:** FastAPI (Python), SQLAlchemy, Uvicorn
- **Frontend:** React + Vite, CSS3 (Vanilla), React Router
- **AI/LLM:** HuggingFace Inference API (Qwen 2.5 7B Instruct)
- **Vector DB:** ChromaDB (Sentence-Transformers)
- **Database:** PostgreSQL (via Supabase or local)
- **Auth:** Firebase Authentication

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- Node.js & npm

### 2. Installation

**Backend Setup:**
```bash
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd frontend
npm install
```

### 3. Configuration (`.env`)
Create a **single `.env` file** in the project root with the following keys:

```env
# AI Brain
HUGGINGFACE_TOKEN="your_hf_token"

# Database (PostgreSQL/Supabase)
POSTGRES_URL="postgresql://user:password@host:5432/postgres"

# Firebase (Frontend)
VITE_FIREBASE_API_KEY="..."
VITE_FIREBASE_AUTH_DOMAIN="..."
VITE_FIREBASE_PROJECT_ID="..."

# Firebase Admin (Backend)
FIREBASE_CREDENTIALS_PATH="firebase-key.json"
```

### 4. Build the RAG Index
Before running the app, index the empathy and knowledge datasets:
```bash
cd backend
python build_rag_index.py
```

### 5. Running the App
**Start Backend:**
```bash
cd backend
python -m src.app.chat_api
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🧑‍💼 Admin Mode
To access the **Counselor Dashboard**, navigate to `/admin` in your browser. This panel allows professional counselors to monitor flagged crisis situations in real-time.

---

## 🔒 Security & Privacy
- **Privacy First:** The counselor cannot see your private chats unless a high-risk situation is detected by the AI.
- **Support-Only:** MyAlly is a support tool, not a clinical diagnosis or therapy service. Always consult a professional for medical advice.
