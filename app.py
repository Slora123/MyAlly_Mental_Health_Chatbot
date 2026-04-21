"""
app.py
───────
MyAlly - Empathetic Student Mental-Health Chatbot
Entry-point. All implementation lives in src/.

Usage:
    python app.py
    (build the vector index first with: python build_rag_index.py)
"""

import uvicorn

if __name__ == "__main__":
    print("MyAlly is starting… http://127.0.0.1:8000")
    uvicorn.run("src.app.chat_api:app", host="127.0.0.1", port=8000, reload=False)
