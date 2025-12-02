from textwrap import dedent
from typing import Iterable, Mapping


def _render_history(history: Iterable[Mapping[str, str]]) -> str:
    snippets = []
    for item in history:
        user = item.get("user_message")
        bot = item.get("bot_response")
        snippets.append(f"User: {user}\nBot: {bot}")
    return "\n\n".join(snippets)


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
