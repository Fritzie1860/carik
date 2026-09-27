import asyncio
from datetime import datetime
from typing import List, Tuple
from domain.models import AuditMetrics, AuditReport, GrammarIssue
from domain.protocols import IPlagiarismChecker, IGrammarChecker, IRoboticLinter


class AuditAggregator:
    """Executes parallel quality audits and constructs comprehensive audit reports."""

    def __init__(
        self,
        plagiarism_checker: IPlagiarismChecker,
        grammar_checker: IGrammarChecker,
        robotic_linter: IRoboticLinter
    ) -> None:
        self.plagiarism_checker = plagiarism_checker
        self.grammar_checker = grammar_checker
        self.robotic_linter = robotic_linter

    def _summarize_feedback(self, metrics: AuditMetrics) -> Tuple[str, List[str]]:
        feedback_lines: List[str] = []
        flagged: List[str] = []

        if metrics.plagiarism_ratio >= 0.08:
            feedback_lines.append(f"- High web overlap similarity ({metrics.plagiarism_ratio * 100:.1f}%). Rephrase sentence structures.")
        if metrics.critical_grammar_errors > 0:
            feedback_lines.append(f"- Found {metrics.critical_grammar_errors} critical grammar/spelling errors.")
            for g in metrics.grammar_issues[:3]:
                feedback_lines.append(f"  * {g.message}")
        if metrics.cliche_matches:
            feedback_lines.append(f"- Banned AI cliches detected: {', '.join(metrics.cliche_matches)}.")
            for c in metrics.detailed_cliches:
                flagged.append(f"Word '{c.word}' in: \"{c.sentence}\" -> Suggested replacement: {c.replacement}")
        if metrics.burstiness_score < 8.5:
            feedback_lines.append(f"- Monotonous cadence (Burstiness standard dev is {metrics.burstiness_score:.1f}, target >= 8.5). Mix short 3-6 word sentences with longer complex ones.")
        if metrics.em_dash_count > 2:
            feedback_lines.append(f"- Em-dash count ({metrics.em_dash_count}) exceeds limit. Replace with periods or commas.")

        summary = "\n".join(feedback_lines) if feedback_lines else "All quality thresholds passed."
        return summary, flagged

    async def evaluate(self, text: str, iteration: int = 1) -> AuditReport:
        # Run plagiarism and grammar checks concurrently
        plag_task = self.plagiarism_checker.check(text)
        gram_task = self.grammar_checker.check(text)
        plag_score, grammar_issues = await asyncio.gather(plag_task, gram_task)

        # Run local heuristic linter synchronously (<2ms)
        linter_data = self.robotic_linter.lint(text)
        critical_count = sum(1 for g in grammar_issues if g.category == "critical")

        metrics = AuditMetrics(
            plagiarism_ratio=plag_score,
            critical_grammar_errors=critical_count,
            grammar_issues=grammar_issues,
            cliche_matches=linter_data.get("cliche_matches", []),
            detailed_cliches=linter_data.get("detailed_cliches", []),
            burstiness_score=linter_data.get("burstiness_score", 0.0),
            sentence_lengths=linter_data.get("sentence_lengths", []),
            em_dash_count=linter_data.get("em_dash_count", 0),
            total_words=linter_data.get("total_words", 0)
        )

        feedback_summary, flagged_sentences = self._summarize_feedback(metrics)
        return AuditReport(
            iteration=iteration,
            metrics=metrics,
            feedback_summary=feedback_summary,
            flagged_sentences=flagged_sentences,
            draft_snapshot=text,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
