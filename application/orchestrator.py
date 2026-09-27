from typing import Optional, Callable, Awaitable
from domain.models import ArticleDraft, PipelineStatus
from domain.protocols import ITranslator, IMultiPassHumanizer
from application.audit_aggregator import AuditAggregator
from application.semantic_guard import SemanticPreservationGuard


ProgressCallback = Optional[Callable[[str, dict], Awaitable[None]]]


class PipelineOrchestrator:
    """Orchestrates the exact flowchart: Stage 1 (Translation) -> Stage 2 (Audit) -> Decision -> Stage 3 (3-Pass Paraphrase) -> Loop."""

    def __init__(
        self,
        translator: ITranslator,
        auditor: AuditAggregator,
        humanizer: IMultiPassHumanizer,
        semantic_guard: Optional[SemanticPreservationGuard] = None,
        max_retries: int = 3
    ) -> None:
        self.translator = translator
        self.auditor = auditor
        self.humanizer = humanizer
        self.guard = semantic_guard or SemanticPreservationGuard()
        self.max_retries = max_retries

    async def _notify(self, callback: ProgressCallback, event: str, draft: ArticleDraft, payload_extra: Optional[dict] = None) -> None:
        if callback:
            data = {
                "status": draft.status.value,
                "current_draft": draft.current_english_draft,
                "history_length": len(draft.iteration_history),
                "latest_report": draft.iteration_history[-1].model_dump() if draft.iteration_history else None,
                "sub_pass_history": [p.model_dump() for p in draft.sub_pass_history]
            }
            if payload_extra:
                data.update(payload_extra)
            await callback(event, data)

    async def _execute_stage_3_multi_pass(self, draft: ArticleDraft, feedback: str, cb: ProgressCallback) -> None:
        # Pass 1: Orwell's 6 Rules (lguz)
        draft.status = PipelineStatus.STAGE_3_PASS_1_ORWELL
        await self._notify(cb, "STAGE_3_PASS_1_START", draft)
        pass1 = await self.humanizer.run_pass_1_orwell(draft.current_english_draft, feedback)
        draft.current_english_draft = pass1.revised_text
        draft.sub_pass_history.append(pass1)
        await self._notify(cb, "STAGE_3_PASS_1_DONE", draft)

        # Pass 2: Rhythm & Syntax Variance (blader)
        draft.status = PipelineStatus.STAGE_3_PASS_2_RHYTHM
        await self._notify(cb, "STAGE_3_PASS_2_START", draft)
        pass2 = await self.humanizer.run_pass_2_rhythm(draft.current_english_draft, feedback)
        draft.current_english_draft = pass2.revised_text
        draft.sub_pass_history.append(pass2)
        await self._notify(cb, "STAGE_3_PASS_2_DONE", draft)

        # Pass 3: Concrete details & anti-generalization (conorbronsdon)
        draft.status = PipelineStatus.STAGE_3_PASS_3_SPECIFICITY
        await self._notify(cb, "STAGE_3_PASS_3_START", draft)
        pass3 = await self.humanizer.run_pass_3_specificity(
            draft.current_english_draft,
            draft.original_bahasa,
            feedback
        )
        draft.current_english_draft = pass3.revised_text
        draft.sub_pass_history.append(pass3)
        await self._notify(cb, "STAGE_3_PASS_3_DONE", draft)

    async def run(self, draft: ArticleDraft, callback: ProgressCallback = None) -> ArticleDraft:
        try:
            # Stage 1: Translation (Apply conorbronsdon style guide)
            draft.status = PipelineStatus.STAGE_1_TRANSLATING
            await self._notify(callback, "STAGE_1_TRANSLATING_START", draft)
            draft.current_english_draft = await self.translator.translate(draft.original_bahasa)
            await self._notify(callback, "STAGE_1_TRANSLATING_DONE", draft)

            # Audit & Paraphrase Loop
            for cycle in range(1, self.max_retries + 1):
                # Stage 2: Deterministic & External Audit
                draft.status = PipelineStatus.STAGE_2_AUDITING
                await self._notify(callback, "STAGE_2_AUDITING_START", draft, {"cycle": cycle})
                report = await self.auditor.evaluate(draft.current_english_draft, iteration=cycle)
                draft.iteration_history.append(report)
                await self._notify(callback, "STAGE_2_AUDITING_DONE", draft, {"cycle": cycle})

                # Decision: All Checks Passed?
                if report.metrics.is_passing:
                    draft.status = PipelineStatus.PASSED
                    await self._notify(callback, "PASSED_READY_ARTICLE", draft)
                    return draft

                # Stage 3: Multi-Pass Paraphrase (if still within budget)
                if cycle < self.max_retries:
                    await self._execute_stage_3_multi_pass(draft, report.feedback_summary, callback)

            draft.status = PipelineStatus.MAX_RETRIES_EXCEEDED
            await self._notify(callback, "MAX_RETRIES_EXCEEDED", draft)
            return draft
        except Exception as err:
            draft.status = PipelineStatus.ERROR
            draft.error_message = str(err)
            await self._notify(callback, "ERROR", draft)
            return draft
