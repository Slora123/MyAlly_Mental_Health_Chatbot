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
    import subprocess
    from pathlib import Path
    
    db_path = Path(__file__).resolve().parents[1] / "database" / "chroma_db"
    if not db_path.exists() or not any(db_path.iterdir()):
        print("⚠️  Vector database missing! Bootstrapping RAG index...")
        
        # Decompress datasets if needed
        data_dir = Path(__file__).resolve().parents[1] / "database" / "data" / "processed"
        for gz_file in data_dir.glob("*.jsonl.gz"):
            print(f"Decompressing {gz_file.name}...")
            subprocess.run(["gzip", "-d", "-f", str(gz_file)], check=False)
            
        build_script = Path(__file__).resolve().parents[1] / "database" / "build_rag_index.py"
        subprocess.run(["python", str(build_script)], check=False)
        print("✅  RAG index bootstrap complete.")

    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 MyAlly is starting on 0.0.0.0:{port}")
    uvicorn.run("src.app.chat_api:app", host="0.0.0.0", port=port, reload=False)
