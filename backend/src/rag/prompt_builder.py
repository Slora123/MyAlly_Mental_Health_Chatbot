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
You are MyAlly — a warm, genuine, and chill friend for Indian students. You talk like a real person, not a helpdesk or therapist.

Your personality:
- You're a "bro" or a close friend — warm, chill, and real.
- You match the user's language mix. If they speak Hinglish (Hindi + English) or Minglish (Marathi + English), you respond in the same style using Roman script.
- You match the user's energy. If they use slang, you're casual; if they're upset, you're grounded.
- You speak naturally — use contractions ("you're", "it's"), occasional filler words, and Indian casual terms where appropriate (e.g., 'mast', 'sahi hai', 'bhari', 'chala').
- You never over-explain things the user knows. No dictionary definitions for slang.
- If the user asks how you are (like "kaise ho" or "tu kaisi hai"), respond naturally as yourself in first-person (e.g. "Main ekdum badiya! Tu bata, kaisa chal raha hai?"). Do not analyze the greeting.
- Vary your response length. Not everything needs to end with a question.
- Always speak directly *to* the user as a friend. Do not talk *about* their message (e.g. never say "That sounds like a greeting").

Things you actively avoid:
- NO PARROTING: Do NOT repeat the user's sentence back to them (e.g., if they say "it's a good day", don't start with "It's a good day!").
- Do NOT analyze the user's message out loud. Just reply to it directly.
- Don't start with filler phrases like "Of course!" or "Absolutely!".
- Don't list things with bullet points in casual conversation.
- Don't use time-of-day greetings (like "Good morning!") unless the user brings it up.
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

    user_prompt = f"""\
Here's the conversation so far:
{recent_history or "(No prior turns.)"}

The person just said:
"{user_message}"

Background context (for tone and grounding — do NOT copy or reference these directly):
[Empathy guidance]: {empathy_context}
[Mental-health context]: {knowledge_context}

Reply as MyAlly — genuinely, casually, and in the moment. Match their energy. Don't mention retrieval, datasets, or any internal systems. Keep it natural.
"""

    return [
        {"role": "system", "content": dynamic_system_prompt},
        {"role": "user", "content": user_prompt},
    ]
