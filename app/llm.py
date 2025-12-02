from textwrap import dedent


def generate_response(user_message: str, context: str | None = None) -> str:
    context_section = f"\nContext: {context}" if context else ""
    return dedent(
        f"""
        Thanks for your question!{context_section}
        Here's a helpful response based on the information we have: {user_message}
        If this doesn't solve your problem, let me know and I can create a ticket for our team.
        """
    ).strip()
