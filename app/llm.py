from textwrap import dedent
from typing import Iterable, Mapping

from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)


def _render_history(history: Iterable[Mapping[str, str]]) -> str:
    snippets = []
    for item in history:
        user = item.get("user_message")
        bot = item.get("bot_response")
        snippets.append(f"User: {user}\nBot: {bot}")
    return "\n\n".join(snippets)


def _build_messages(user_message: str, context: str | None, history: Iterable[Mapping[str, str]] | None) -> list[dict[str, str]]:
    system_prompt = dedent(
        """
        You are a concise and polite customer support assistant. Use the provided FAQ context and
        recent conversation to answer the user's question. If you do not have enough information,
        ask a brief clarifying question and mention that you can escalate to a human agent if needed.
        Keep responses under 120 words.
        """
    ).strip()

    history_section = _render_history(history) if history else None

    user_parts = [f"Customer question: {user_message}"]
    if context:
        user_parts.append(f"FAQ context: {context}")
    if history_section:
        user_parts.append(f"Recent history (most recent first):\n{history_section}")

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]


def _fallback_response(user_message: str, context: str | None, history: Iterable[Mapping[str, str]] | None) -> str:
def generate_response(
    user_message: str,
    context: str | None = None,
    history: Iterable[Mapping[str, str]] | None = None,
) -> str:
    context_section = f"\nContext: {context}" if context else ""
    history_section = f"\nPrevious conversation (most recent first):\n{_render_history(history)}" if history else ""
    return dedent(
        f"""
        Thanks for your question!{context_section}{history_section}
        Here's a helpful response based on the information we have: {user_message}
        If this doesn't solve your problem, let me know and I can create a ticket for our team.
        """
    ).strip()


def generate_response(
    user_message: str,
    context: str | None = None,
    history: Iterable[Mapping[str, str]] | None = None,
) -> str:
    if not OPENAI_API_KEY:
        return _fallback_response(user_message, context, history)

    try:
        messages = _build_messages(user_message, context, history)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.4,
        )
        content = completion.choices[0].message.content
        return content.strip() if content else _fallback_response(user_message, context, history)
    except Exception:
        return _fallback_response(user_message, context, history)
