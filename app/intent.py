from typing import Tuple


INTENT_KEYWORDS = {
    "refund": ["refund", "return", "money back"],
    "order_tracking": ["track", "tracking", "where is my order"],
    "account_help": ["account", "login", "password"],
    "escalation": ["agent", "human", "representative", "escalate"],
}


def detect_intent(message: str) -> Tuple[str, float]:
    text = message.lower()
    best_intent = "general"
    best_score = 0.0

    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text) / max(len(keywords), 1)
        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent, best_score
