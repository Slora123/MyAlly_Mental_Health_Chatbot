"""
src/app/service.py
───────────────────
Section 12 of the Implementation Guide: Backend responsibilities.

Orchestrates the full query-time RAG pipeline:
  1. Pre-generation safety check  →  crisis path if high-risk
  2. Intent classification          →  router.py
  3. Empathy retrieval              →  retriever.py
  4. Conditional knowledge retrieval
  5. Prompt assembly                →  prompt_builder.py
  6. LLM generation                 →  huggingface_hub InferenceClient
  7. Post-generation safety check   →  safety.py
  8. Logging                        →  app/logging.py
"""

from __future__ import annotations

import os

import chromadb
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from src.app import logging as app_logging
from src.rag import retriever, prompt_builder, router, safety
from src.rag.embeddings import get_embedding_function

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
DB_PATH = str((
    __import__("pathlib").Path(__file__).resolve().parents[3] / "database" / "chroma_db"
))
EMPATHY_COLLECTION_NAME = "student_support_empathy"
KNOWLEDGE_COLLECTION_NAME = "student_support_knowledge"


def _ensure_hf_token() -> None:
    if not HF_TOKEN:
        raise RuntimeError(
            "HUGGINGFACE_TOKEN is missing. Add it to a .env file before running."
        )


# ── Lazy-loaded singletons ────────────────────────────────────────────────────
_client: InferenceClient | None = None
_empathy_col: chromadb.Collection | None = None
_knowledge_col: chromadb.Collection | None = None


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        _ensure_hf_token()
        _client = InferenceClient(model=MODEL_NAME, token=HF_TOKEN)
    return _client


def _get_collections() -> tuple[chromadb.Collection, chromadb.Collection]:
    global _empathy_col, _knowledge_col
    if _empathy_col is None or _knowledge_col is None:
        chroma = chromadb.PersistentClient(path=DB_PATH)
        ef = get_embedding_function()
        _empathy_col = chroma.get_or_create_collection(
            name=EMPATHY_COLLECTION_NAME, embedding_function=ef
        )
        _knowledge_col = chroma.get_or_create_collection(
            name=KNOWLEDGE_COLLECTION_NAME, embedding_function=ef
        )
    return _empathy_col, _knowledge_col


def _require_index(empathy_col: chromadb.Collection, knowledge_col: chromadb.Collection) -> None:
    if empathy_col.count() == 0 or knowledge_col.count() == 0:
        raise RuntimeError(
            "The vector database is empty. Run `python build_rag_index.py` first."
        )


# ── Crisis response ───────────────────────────────────────────────────────────

_CRISIS_REPLY = (
    "It sounds like you may be in immediate distress, and I'm really glad you "
    "said it here. Please contact a trusted person, your campus counselor, or a "
    "local emergency or crisis service right now. If you feel you might act on "
    "thoughts of harming yourself or someone else, call your local emergency "
    "number immediately or go to the nearest emergency room. If you want, you "
    "can message me the name of one safe person you can reach out to next."
)


# ── Main chat logic ───────────────────────────────────────────────────────────

def chat_logic(user_message: str, history: list) -> str:
    """
    Full RAG pipeline entry-point consumed by the Gradio ChatInterface.

    Parameters
    ----------
    user_message : The student's current message.
    history      : Gradio conversation history.

    Returns
    -------
    The assistant reply string.
    """
    empathy_col, knowledge_col = _get_collections()

    try:
        _require_index(empathy_col, knowledge_col)
    except RuntimeError as exc:
        return str(exc)

    # ── Step 1: Pre-generation safety check ──────────────────────────────────
    is_safe, _ = safety.check_pre_generation(user_message)
    intent = router.classify_intent(user_message)

    if not is_safe or intent == "high_risk":
        app_logging.append_log(
            app_logging.make_log_entry(
                user_query=user_message,
                ai_response=_CRISIS_REPLY,
                intent="high_risk",
                retrieved_empathy_ids=[],
                retrieved_knowledge_ids=[],
                retrieved_empathy_metadata=[],
                retrieved_knowledge_metadata=[],
                mode="crisis",
            )
        )
        return _CRISIS_REPLY

    # ── Step 2: Retrieval ─────────────────────────────────────────────────────
    empathy_items = retriever.retrieve_empathy_examples(empathy_col, user_message)

    fetch_knowledge = intent in ("knowledge_seeking", "mixed")
    knowledge_items = (
        retriever.retrieve_knowledge_snippets(knowledge_col, user_message)
        if fetch_knowledge
        else []
    )

    # ── Step 3: Prompt assembly ───────────────────────────────────────────────
    empathy_ctx = retriever.render_empathy_context(empathy_items)
    knowledge_ctx = retriever.render_knowledge_context(knowledge_items)
    messages = prompt_builder.build_messages(
        user_message, history, empathy_ctx, knowledge_ctx
    )

    # ── Step 4: Generation ────────────────────────────────────────────────────
    try:
        response = _get_client().chat_completion(
            messages=messages,
            max_tokens=400,
            temperature=0.8,
        )
        ai_reply: str = " ".join(
            response.choices[0].message.content.split()
        )
    except Exception as exc:
        return f"Model error: {exc}"

    # ── Step 5: Post-generation safety check ─────────────────────────────────
    reply_safe, safety_issues = safety.check_post_generation(ai_reply)
    # Log issues but do not block: add a gentle disclaimer instead
    if not reply_safe:
        ai_reply += (
            "\n\n_(Please remember: I'm a support assistant, not a therapist or "
            "medical professional. For clinical advice, reach out to a qualified "
            "professional.)_"
        )

    # ── Step 6: Logging ───────────────────────────────────────────────────────
    app_logging.append_log(
        app_logging.make_log_entry(
            user_query=user_message,
            ai_response=ai_reply,
            intent=intent,
            retrieved_empathy_ids=[item["id"] for item in empathy_items],
            retrieved_knowledge_ids=[item["id"] for item in knowledge_items],
            retrieved_empathy_metadata=[item["metadata"] for item in empathy_items],
            retrieved_knowledge_metadata=[item["metadata"] for item in knowledge_items],
            safety_issues=safety_issues,
            mode="support_plus_rag",
        )
    )

    return ai_reply
