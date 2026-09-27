import re
from typing import Dict, List, Tuple
import numpy as np
from domain.models import ClicheMatch


CLICHE_REPLACEMENTS: Dict[str, str] = {
    "delve": "examine, explore, or study",
    "tapestry": "structure, blend, or mix",
    "testament": "evidence or proof",
    "beacon": "guide or model",
    "pivotal": "central, key, or critical",
    "multifaceted": "complex or varied",
    "fostering": "encouraging or building",
    "foster": "encourage or build",
    "unlock": "reveal or enable",
    "unlocking": "revealing or enabling",
    "furthermore": "also, besides, or cut entirely",
    "in conclusion": "finally, or cut entirely",
    "moreover": "also, or cut entirely",
    "it is important to note": "note that, or cut entirely",
    "seamlessly": "smoothly or easily",
    "vibrant": "active, lively, or bright",
    "landscape": "field, context, or industry",
    "harnessing": "using or applying",
    "harness": "use or apply",
    "paradigm": "model, pattern, or framework",
    "game-changer": "major shift or breakthrough",
    "plethora": "many, plenty, or excess",
    "overarching": "general or broad",
    "elevate": "raise or improve",
    "elevates": "raises or improves",
    "elevating": "raising or improving",
    "embark": "start or begin",
    "embarks": "starts or begins",
    "embarking": "starting or beginning",
    "navigate": "handle, manage, or steer",
    "navigating": "handling, managing, or steering",
    "realm": "area, field, or world",
    "cornerstone": "basis, foundation, or root",
    "revolutionize": "transform or overhaul",
    "revolutionizing": "transforming or overhauling",
}


class HeuristicRoboticLinter:
    """Detects AI writing cliches, em-dash abuse, and computes sentence burstiness."""

    def __init__(self) -> None:
        patterns = [re.escape(word) for word in CLICHE_REPLACEMENTS.keys()]
        self._cliche_regex = re.compile(
            r"\b(" + "|".join(patterns) + r")\b",
            re.IGNORECASE
        )
        self._em_dash_regex = re.compile(r"(—| - |--)", re.UNICODE)
        self._sentence_regex = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")

    def split_sentences(self, text: str) -> List[str]:
        raw_chunks = self._sentence_regex.split(text.strip())
        return [s.strip() for s in raw_chunks if s.strip()]

    def count_em_dashes(self, text: str) -> int:
        if not text:
            return 0
        return len(self._em_dash_regex.findall(text))

    def _find_cliches_in_sentence(self, sentence: str) -> List[ClicheMatch]:
        matches: List[ClicheMatch] = []
        for match in self._cliche_regex.finditer(sentence):
            matched_word = match.group(0).lower()
            replacement = CLICHE_REPLACEMENTS.get(matched_word, "use simpler word")
            matches.append(ClicheMatch(
                word=match.group(0),
                replacement=replacement,
                sentence=sentence
            ))
        return matches

    def detect_cliches(self, text: str) -> Tuple[List[str], List[ClicheMatch]]:
        if not text:
            return [], []
        sentences = self.split_sentences(text)
        all_matches: List[ClicheMatch] = []
        unique_words: set = set()
        for sentence in sentences:
            found = self._find_cliches_in_sentence(sentence)
            all_matches.extend(found)
            for m in found:
                unique_words.add(m.word.lower())
        return sorted(list(unique_words)), all_matches

    def calculate_burstiness(self, sentences: List[str]) -> Tuple[float, List[int], int]:
        if not sentences:
            return 0.0, [], 0
        lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
        valid_lengths = [l for l in lengths if l > 0]
        if len(valid_lengths) <= 1:
            return 0.0, valid_lengths, sum(valid_lengths)
        std_dev = float(np.std(valid_lengths, ddof=0))
        return round(std_dev, 2), valid_lengths, sum(valid_lengths)

    def lint(self, text: str) -> dict:
        sentences = self.split_sentences(text)
        unique_cliches, detailed_cliches = self.detect_cliches(text)
        em_dash_count = self.count_em_dashes(text)
        burstiness, lengths, total_words = self.calculate_burstiness(sentences)
        return {
            "cliche_matches": unique_cliches,
            "detailed_cliches": detailed_cliches,
            "em_dash_count": em_dash_count,
            "burstiness_score": burstiness,
            "sentence_lengths": lengths,
            "total_words": total_words,
            "sentence_count": len(sentences),
        }
