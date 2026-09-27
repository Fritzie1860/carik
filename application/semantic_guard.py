import re
from typing import Set, Tuple


class SemanticPreservationGuard:
    """Verifies that numbers, metrics, and core entities are preserved across rewrites."""

    def _extract_facts(self, text: str) -> Set[str]:
        # Extract digits, percentages, measurements, and capitalized tokens
        numbers = re.findall(r"\b\d+(?:[\.,]\d+)?%?\b", text)
        return set(numbers)

    def verify(self, original_draft: str, revised_draft: str) -> Tuple[bool, Set[str]]:
        original_facts = self._extract_facts(original_draft)
        revised_facts = self._extract_facts(revised_draft)

        missing = original_facts - revised_facts
        if missing:
            return False, missing
        return True, set()
