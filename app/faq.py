import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FAQService:
    def __init__(self, faq_path: Path) -> None:
        self.faq_path = faq_path
        self.faqs: List[Dict[str, str]] = []

    def load(self) -> None:
        if not self.faq_path.exists():
            raise FileNotFoundError(f"FAQ file not found at {self.faq_path}")
        with self.faq_path.open("r", encoding="utf-8") as file:
            self.faqs = json.load(file)

    def best_match(self, query: str) -> Tuple[Optional[str], float]:
        if not self.faqs:
            return None, 0.0

        normalized_query = query.lower().strip()
        best_answer: Optional[str] = None
        best_score = 0.0

        for entry in self.faqs:
            question = entry.get("question", "").lower().strip()
            answer = entry.get("answer")
            if not answer:
                continue

            score = SequenceMatcher(None, normalized_query, question).ratio()
            if score > best_score:
                best_score = score
                best_answer = answer

        return best_answer, best_score
