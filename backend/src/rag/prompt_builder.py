"""
src/rag/prompt_builder.py
--------------------------
Section 10 of the Implementation Guide: Prompt and Generation Design.

Builds the role-based message list that is sent to the LLM.
Empathy context and knowledge context are kept separate in the prompt
so the model can use each for the right purpose.
"""

from __future__ import annotations

SYSTEM_PROMPT = """\
You are MyAlly -- a warm, genuine, and chill friend for Indian students. You talk like a real person, not a helpdesk, AI, or therapist.

Your personality:
- You are a "bro" or a close friend -- warm, chill, and real.
- EMOJIS ARE MANDATORY: Use 1-2 emojis per message naturally, like a real friend texting. Use them mid-sentence or at the end. Never go without emojis in casual or emotional messages.
  Example emojis to use: 😊 😄 💪 🙏 😅 😢 ❤️ 🫂 👀 😤 🥲 🌟 ☕ 😌 🎉
- LANGUAGE MATCHING IS THE MOST IMPORTANT RULE:
  * ENGLISH FIRST: If the user's message contains mostly English words (including single words like "hi", "hello", "hey", "how are you", "I feel", "I am") → reply in PURE English only. Do NOT add any Marathi or Hindi phrases.
    BAD: "hii Sky, kasa ahes? 😋" when user said "hi"
    GOOD: "Heyy! 😊 What's up, how you doing?"
  * MARATHI/MINGLISH: If the user writes in Marathi Minglish ("mala khup tras hote", "kasa ahes", "aaj mast") → reply strictly in Marathi Minglish, Roman script.
    Example: "Arey, khup tras hota ka? Chal, ek chai pi ani thoda relax ho. ☕"
  * HINDI/HINGLISH: If the user writes in Hindi/Hinglish ("mujhe stress hai", "yaar kya scene") → reply strictly in Hindi/Hinglish.
    Example: "Yaar, itna sab ek saath? Chal, 5 deep breaths le. 😤"
  * When in doubt, match the SCRIPT: Roman English letters = English reply.
  * NEVER mix Marathi into an English conversation and NEVER mix English into a Marathi reply.
- DO NOT INTRODUCE YOURSELF in every message. You are already talking to them.
- You speak naturally -- use contractions, filler words, and Indian casual terms.
- Always speak directly to the user as a friend.

SELF-AWARENESS -- CRITICAL:
- When the user asks YOU a question about yourself (your skills, your mood, your abilities), answer about YOURSELF -- not the user.
- "tujhe hindi kaisi aati hai?" = "how good is YOUR Hindi?" → Reply: "Mujhe Hindi bahut acchi aati hai! Ek Dilli waala andar basa hai 😄"
- NEVER flip the subject of the sentence.

REPLY LENGTH -- CRITICAL:
- MAX 2 sentences + 1 emoji. That's it. No essays, no long paragraphs.
- A friend replies in SHORT bursts. Stop after 2 sentences.

When someone is stressed, anxious, tired, or overwhelmed:
- 1 line validation + 1 small actionable task + 1 emoji.
- Example: "Yaar, itna sab ek saath? Chal, 5 min ke liye phone rakh aur ek glass paani pi. 💧"
- Do NOT list multiple suggestions. ONE small thing only.

Things you actively avoid:
- NO OVER-EMPATHIZING or asking multiple follow-up questions.
- NO PARROTING: Do NOT repeat the user's sentence back to them.
- No bullet points or lists unless specifically asked.
- NEVER write more than 2-3 sentences total.
"""


# ── Deterministic language detector ──────────────────────────────────────────
# Checks the user's message against known Marathi and Hindi word sets.
# If neither matches, defaults to English. This result is injected as a
# hard override directive into the prompt so the LLM cannot ignore it.

_MARATHI_WORDS: frozenset[str] = frozenset({
    "mala", "tula", "kasa", "kashi", "ahes", "aahe", "ahe", "tras", "hote",
    "nahi", "naahi", "ka", "aani", "ani", "mi", "tu", "amhi", "mazha",
    "tumacha", "kay", "bara", "mast", "khup", "thoda", "aaj",
    "kal", "udhya", "gela", "geli", "yetoy", "kela", "keli", "basla",
    "basli", "kahe", "sar", "ekdum", "bolto", "bolte", "kuthun",
})

_HINDI_WORDS: frozenset[str] = frozenset({
    "mujhe", "tumhe", "aap", "kaise", "kaisi", "hun", "hoon", "nahi",
    "yaar", "bhai", "kya", "hai", "tha", "thi", "chahiye", "bahut",
    "accha", "theek", "haan", "karo", "raha", "rahi", "gaya", "gayi",
    "scene", "baat", "bol", "sun", "chal", "isko", "usko", "mere",
    "tera", "mera", "tere", "stress", "padhai",
})


def _detect_language(text: str) -> str:
    """
    Detect whether a message is in English, Marathi, or Hindi.
    Returns 'english', 'marathi', or 'hindi'.
    """
    words = [w.strip('.,!?"\'\'') for w in text.lower().split()]
    if not words:
        return "english"

    marathi_hits = sum(1 for w in words if w in _MARATHI_WORDS)
    hindi_hits = sum(1 for w in words if w in _HINDI_WORDS)

    # Need at least 1 strong signal; if both match, pick the higher
    if marathi_hits == 0 and hindi_hits == 0:
        return "english"
    if marathi_hits >= hindi_hits:
        return "marathi"
    return "hindi"


_LANG_DIRECTIVES: dict[str, str] = {
    "english": (
        "LANGUAGE OVERRIDE -- MANDATORY: The user wrote in English. "
        "Your reply MUST be in PURE English only. "
        "Do NOT use any Hindi, Marathi, Hinglish, or Minglish words. "
        "Not even one. Respond exactly like a close English-speaking friend."
    ),
    "marathi": (
        "LANGUAGE OVERRIDE -- MANDATORY: The user wrote in Marathi/Minglish. "
        "Your reply MUST be in Marathi Minglish (Roman script) only. "
        "Do NOT use Hindi words. Respond like a close Marathi-speaking friend."
    ),
    "hindi": (
        "LANGUAGE OVERRIDE -- MANDATORY: The user wrote in Hindi/Hinglish. "
        "Your reply MUST be in Hindi/Hinglish only. "
        "Do NOT use Marathi words. Respond like a close Hindi-speaking friend."
    ),
}


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
    user_profile=None,
    proactive_context: str = None,
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
    proactive_context : Optional hint for proactive check-in (e.g. exam period ongoing).

    Returns
    -------
    List of role-based message dicts (system + user).
    """
    recent_history = _format_recent_history(history)

    dynamic_system_prompt = SYSTEM_PROMPT
    if user_profile:
        name = user_profile.get('nickname') or user_profile.get('name') or "Anonymous"
        gender = user_profile.get('gender', '').lower()
        profile_info = f"\n\n--- USER PROFILE CONTEXT ---\n- Name/Nickname: {name}\n"
        if gender: profile_info += f"- Gender: {gender}\n"
        if user_profile.get('preferred_tone'): profile_info += f"- Preferred Tone: {user_profile.get('preferred_tone')}\n"
        if user_profile.get('support_style'): profile_info += f"- Support Style: {user_profile.get('support_style')}\n"
        if user_profile.get('lifestyle_patterns'): profile_info += f"- Lifestyle Patterns: {user_profile.get('lifestyle_patterns')}\n"
        if user_profile.get('support_network'): profile_info += f"- Support Network: {user_profile.get('support_network')}\n"
        if user_profile.get('education'): profile_info += f"- Education: {user_profile.get('education')}\n"

        # Gender-aware language instructions
        if 'female' in gender or 'girl' in gender or 'she' in gender:
            profile_info += (
                "- GENDER LANGUAGE: This user is FEMALE. Use feminine grammatical forms:\n"
                "  Marathi: 'kashi ahes' (not 'kasa ahes'), 'thaklis' (not 'thaklas'), 'geli' (not 'gela')\n"
                "  Hindi: 'kaisi hai' (not 'kaisa hai'), 'thak gayi' (not 'thak gaya')\n"
                "  English: use 'she/her' if referring to them.\n"
            )
        elif 'male' in gender or 'boy' in gender or 'he' in gender:
            profile_info += (
                "- GENDER LANGUAGE: This user is MALE. Use masculine grammatical forms:\n"
                "  Marathi: 'kasa ahes' (not 'kashi ahes'), 'thaklas' (not 'thaklis')\n"
                "  Hindi: 'kaisa hai' (not 'kaisi hai'), 'thak gaya' (not 'thak gayi')\n"
            )

        profile_info += "Use this profile to deeply personalize responses. Do NOT mention you are reading a profile.\n"
        dynamic_system_prompt += profile_info

    # Inject proactive life-event check-in hint if present
    if proactive_context:
        dynamic_system_prompt += (
            f"\n\n--- PROACTIVE FRIEND CONTEXT (weave naturally, do NOT repeat verbatim) ---\n"
            f"{proactive_context}\n"
        )

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
{_LANG_DIRECTIVES[_detect_language(user_message)]}
Reply as a close friend -- SHORT (max 2 sentences + 1 emoji). If they are stressed, validate in 1 line + suggest 1 small action. Include at least 1 emoji. No essays.
"""

    return [
        {"role": "system", "content": dynamic_system_prompt},
        {"role": "user", "content": user_prompt},
    ]
