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
    import os
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 MyAlly is starting on 0.0.0.0:{port}")
    uvicorn.run("src.app.chat_api:app", host="0.0.0.0", port=port, reload=False)
