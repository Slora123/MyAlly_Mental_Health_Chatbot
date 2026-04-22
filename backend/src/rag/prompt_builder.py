"""
src/rag/prompt_builder.py
──────────────────────────
Section 10 of the Implementation Guide: Prompt and Generation Design.

Builds the role-based message list that is sent to the LLM.
Empathy context and knowledge context are kept separate in the prompt
(Step 9.5) so the model can use each for the right purpose.
"""

from __future__ import annotations

SYSTEM_PROMPT = """\
You are MyAlly — a warm, genuine, and chill friend for Indian students. You talk like a real person, not a helpdesk, AI, or therapist.

Your personality:
- You're a "bro" or a close friend — warm, chill, and real.
- LANGUAGE MATCHING IS CRITICAL: Always match the user's language mix. If they speak Marathi/Minglish ("Kashi ahes tu"), respond in Marathi/Minglish. If they speak Hindi/Hinglish, respond in Hindi/Hinglish. Use Roman script.
- If the user just says "Hi" or "How are you", give a SHORT, casual reply. Do NOT start a therapy session.
- If the user asks how you are, KEEP IT SHORT and answer as yourself (e.g. "Ekdum mast! Tu bata, kya scene?", "Main badiya hoon, tu bata?"). NEVER assume they are feeling low.
- DO NOT INTRODUCE YOURSELF: Don't say "It's me, MyAlly" or "I am MyAlly" in every message. You're already talking to them.
- You speak naturally — use contractions, occasional filler words, and Indian casual terms.
- Always speak directly *to* the user as a friend. Do NOT analyze their message.

Things you actively avoid:
- NO OVER-EMPATHIZING: Don't jump into "deep talk" or "how are you feeling" unless the user starts a serious conversation.
- NO PARROTING: Do NOT repeat the user's sentence back to them.
- Don't use bullet points or list things unless specifically asked.
- Avoid formal greetings or helpdesk-style introductions.
"""


def _format_recent_history(history: list, limit: int = 3) -> str:
    """
    Format the last `limit` turns of conversation history as a plain-text block.

    Accepts both dict-style turns (Gradio 4+) and list/tuple turns (legacy).
    """
    formatted: list[str] = []
    for turn in history[-limit:]:
        if isinstance(turn, dict):
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role and content:
                formatted.append(f"{role.title()}: {content}")
        elif isinstance(turn, (list, tuple)) and len(turn) >= 2:
            formatted.append(f"User: {turn[0]}")
            formatted.append(f"Assistant: {turn[1]}")
    return "\n".join(formatted)


def build_messages(
    user_message: str,
    history: list,
    empathy_context: str,
    knowledge_context: str,
    user_profile=None
) -> list[dict]:
    """
    Assemble the full message list for the LLM.

    Parameters
    ----------
    user_message      : The student's latest message.
    history           : Gradio chat history (list of dicts or tuples).
    empathy_context   : Pre-rendered empathy examples string.
    knowledge_context : Pre-rendered knowledge snippets string.
    user_profile      : The user's database profile (optional).

    Returns
    -------
    List of role-based message dicts (system + user).
    """
    recent_history = _format_recent_history(history)
    
    dynamic_system_prompt = SYSTEM_PROMPT
    if user_profile:
        name = getattr(user_profile, 'nickname', None) or getattr(user_profile, 'name', None) or "Anonymous"
        profile_info = f"\n\n--- USER PROFILE CONTEXT ---\n- Name/Nickname: {name}\n"
        if getattr(user_profile, 'gender', None): profile_info += f"- Gender: {user_profile.gender}\n"
        if getattr(user_profile, 'preferred_tone', None): profile_info += f"- Preferred Tone: {user_profile.preferred_tone}\n"
        if getattr(user_profile, 'support_style', None): profile_info += f"- Support Style: {user_profile.support_style}\n"
        if getattr(user_profile, 'lifestyle_patterns', None): profile_info += f"- Lifestyle Patterns: {user_profile.lifestyle_patterns}\n"
        if getattr(user_profile, 'support_network', None): profile_info += f"- Support Network: {user_profile.support_network}\n"
        if getattr(user_profile, 'education', None): profile_info += f"- Education: {user_profile.education}\n"
        profile_info += "Use this information to deeply personalize your responses. Match their preferred tone and consider their lifestyle and support network when offering advice or comfort. Do NOT mention you are reading a profile.\n"
        dynamic_system_prompt += profile_info

    context_block = ""
    if empathy_context or knowledge_context:
        context_block = "\nBackground context (for tone and grounding):\n"
        if empathy_context: context_block += f"[Empathy examples]: {empathy_context}\n"
        if knowledge_context: context_block += f"[Related info]: {knowledge_context}\n"

    user_prompt = f"""\
Here's the conversation so far:
{recent_history or "(No prior turns.)"}

The person just said:
"{user_message}"
{context_block}
Reply as a close friend — warm, chill, and matching their energy perfectly. Match their language. Don't mention datasets or systems. Just talk to them.
"""

    return [
        {"role": "system", "content": dynamic_system_prompt},
        {"role": "user", "content": user_prompt},
    ]
