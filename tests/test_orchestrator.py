import pytest
from domain.models import ArticleDraft, PipelineStatus
from infrastructure.heuristic_linter import HeuristicRoboticLinter
from infrastructure.gemini_client import GeminiClient
from infrastructure.gemini_translator import GeminiTranslator
from infrastructure.orwell_humanizer import OrwellHumanizer
from application.audit_aggregator import AuditAggregator
from application.orchestrator import PipelineOrchestrator


class MockPlagiarismChecker:
    async def check(self, text: str) -> float:
        return 0.02


class MockGrammarChecker:
    async def check(self, text: str):
        return []


@pytest.mark.asyncio
async def test_orchestrator_pipeline_flow():
    client = GeminiClient()
    translator = GeminiTranslator(client)
    humanizer = OrwellHumanizer(client)
    plag = MockPlagiarismChecker()
    grammar = MockGrammarChecker()
    linter = HeuristicRoboticLinter()
    
    auditor = AuditAggregator(plag, grammar, linter)
    orchestrator = PipelineOrchestrator(translator, auditor, humanizer, max_retries=2)
    
    draft = ArticleDraft(original_bahasa="Kecerdasan buatan membantu penulisan kode.")
    result = await orchestrator.run(draft)
    
    assert result.status in (PipelineStatus.PASSED, PipelineStatus.MAX_RETRIES_EXCEEDED)
    assert len(result.current_english_draft) > 0
    assert len(result.iteration_history) >= 1
