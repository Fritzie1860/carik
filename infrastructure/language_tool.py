import re
from typing import List
from domain.models import GrammarIssue


COMMON_TYPOS = {
    "teh": "the",
    "recieved": "received",
    "seperate": "separate",
    "untill": "until",
    "occured": "occurred",
    "accomodate": "accommodate",
    "definately": "definitely",
    "goverment": "government",
}


class LanguageToolGrammarChecker:
    """Grammar and spelling audit using language_tool_python with lightweight local fallback."""

    def __init__(self) -> None:
        self._tool = None
        self._init_attempted = False

    def _get_tool(self):
        if not self._init_attempted:
            self._init_attempted = True
            try:
                import language_tool_python
                self._tool = language_tool_python.LanguageTool('en-US')
            except Exception:
                self._tool = None
        return self._tool

    def _fallback_check(self, text: str) -> List[GrammarIssue]:
        issues: List[GrammarIssue] = []
        words = re.findall(r"\b\w+\b", text)
        for i, word in enumerate(words):
            lower_w = word.lower()
            if lower_w in COMMON_TYPOS:
                issues.append(GrammarIssue(
                    message=f"Possible typo: '{word}' -> '{COMMON_TYPOS[lower_w]}'",
                    rule_id="SPELLING_TYPO",
                    offset=0,
                    length=len(word),
                    category="critical",
                    suggestions=[COMMON_TYPOS[lower_w]]
                ))
        # Match genuine duplicate words like 'the the', ignoring valid duplicates
        for match in re.finditer(r"\b([a-zA-Z]{3,})\s+\1\b", text, re.IGNORECASE):
            dup_word = match.group(1)
            if dup_word.lower() not in ("that", "had", "can"):
                issues.append(GrammarIssue(
                    message=f"Repeated word: '{dup_word}'",
                    rule_id="DUPLICATE_WORD",
                    offset=match.start(),
                    length=len(match.group(0)),
                    category="critical",
                    suggestions=[dup_word]
                ))
        return issues

    async def check(self, text: str) -> List[GrammarIssue]:
        if not text.strip():
            return []
        tool = self._get_tool()
        if not tool:
            return self._fallback_check(text)

        try:
            matches = tool.check(text)
            issues: List[GrammarIssue] = []
            for m in matches:
                # Filter out pure style suggestions, keep spelling & grammatical errors
                is_critical = m.ruleIssueType in ("misspelling", "grammar", "duplication")
                if is_critical or "MORFOLOGIK_RULE" in m.ruleId:
                    issues.append(GrammarIssue(
                        message=m.message,
                        rule_id=m.ruleId,
                        offset=m.offset,
                        length=m.errorLength,
                        category="critical" if is_critical else "style",
                        suggestions=m.replacements[:3]
                    ))
            return issues
        except Exception:
            return self._fallback_check(text)
