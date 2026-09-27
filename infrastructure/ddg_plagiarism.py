import re
import random
from typing import List, Set


class DuckDuckGoPlagiarismChecker:
    """Zero-cost plagiarism checker using DuckDuckGo search queries on sampled n-grams."""

    def __init__(self, ngram_size: int = 7, sample_count: int = 5) -> None:
        self.ngram_size = ngram_size
        self.sample_count = sample_count

    def _extract_words(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def _generate_ngrams(self, words: List[str]) -> List[str]:
        if len(words) < self.ngram_size:
            return [" ".join(words)] if words else []
        return [
            " ".join(words[i:i + self.ngram_size])
            for i in range(0, len(words) - self.ngram_size + 1, max(1, self.ngram_size // 2))
        ]

    def _calculate_jaccard(self, query_tokens: Set[str], snippet_tokens: Set[str]) -> float:
        if not query_tokens or not snippet_tokens:
            return 0.0
        intersection = len(query_tokens.intersection(snippet_tokens))
        union = len(query_tokens.union(snippet_tokens))
        return intersection / union if union > 0 else 0.0

    def _sync_ddg_query(self, query: str) -> List[str]:
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            with DDGS(timeout=3) as ddgs:
                results = list(ddgs.text(f'"{query}"', max_results=2))
                return [r.get("body", "") for r in results if isinstance(r, dict)]
        except Exception:
            return []

    async def _search_ddg(self, query: str) -> List[str]:
        import asyncio
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._sync_ddg_query, query),
                timeout=2.0
            )
        except Exception:
            return []

    async def check(self, text: str) -> float:
        words = self._extract_words(text)
        if len(words) < self.ngram_size:
            return 0.0

        all_ngrams = self._generate_ngrams(words)
        if not all_ngrams:
            return 0.0

        sample_k = min(3, len(all_ngrams))
        sampled = random.sample(all_ngrams, sample_k)
        
        matches = 0
        for ngram in sampled:
            snippets = await self._search_ddg(ngram)
            ngram_set = set(ngram.split())
            if any(self._calculate_jaccard(ngram_set, set(self._extract_words(s))) > 0.6 for s in snippets):
                matches += 1

        score = matches / sample_k if sample_k > 0 else 0.0
        return round(score, 3)
