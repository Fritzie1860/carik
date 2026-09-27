from typing import Protocol, List
from .models import AuditMetrics, GrammarIssue, SubPassResult


class ITranslator(Protocol):
    async def translate(self, text: str) -> str:
        """Translate Bahasa Indonesia text into natural English draft applying conorbronsdon style guide."""
        ...


class IPlagiarismChecker(Protocol):
    async def check(self, text: str) -> float:
        """Calculate web overlap similarity score (0.0 to 1.0)."""
        ...


class IGrammarChecker(Protocol):
    async def check(self, text: str) -> List[GrammarIssue]:
        """Detect critical grammatical and spelling errors."""
        ...


class IRoboticLinter(Protocol):
    def lint(self, text: str) -> dict:
        """Detect AI cliches, em-dash abuse, and sentence burstiness."""
        ...


class IMultiPassHumanizer(Protocol):
    async def run_pass_1_orwell(self, text: str, feedback: str) -> SubPassResult:
        """Pass 1: George Orwell's 6 rules (lguz)."""
        ...

    async def run_pass_2_rhythm(self, text: str, feedback: str) -> SubPassResult:
        """Pass 2: Rhythm & Syntax Variance (blader)."""
        ...

    async def run_pass_3_specificity(self, text: str, original_draft: str, feedback: str) -> SubPassResult:
        """Pass 3: Concrete details & anti-generalization (conorbronsdon)."""
        ...
