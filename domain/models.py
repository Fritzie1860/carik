from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    INITIALIZING = "INITIALIZING"
    STAGE_1_TRANSLATING = "STAGE_1_TRANSLATING"
    STAGE_2_AUDITING = "STAGE_2_AUDITING"
    STAGE_3_PASS_1_ORWELL = "STAGE_3_PASS_1_ORWELL"
    STAGE_3_PASS_2_RHYTHM = "STAGE_3_PASS_2_RHYTHM"
    STAGE_3_PASS_3_SPECIFICITY = "STAGE_3_PASS_3_SPECIFICITY"
    PASSED = "PASSED"
    MAX_RETRIES_EXCEEDED = "MAX_RETRIES_EXCEEDED"
    ERROR = "ERROR"


class GrammarIssue(BaseModel):
    message: str
    rule_id: str
    offset: int = 0
    length: int = 0
    category: str = "critical"
    suggestions: List[str] = Field(default_factory=list)


class ClicheMatch(BaseModel):
    word: str
    replacement: str
    sentence: str


class AuditMetrics(BaseModel):
    plagiarism_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    critical_grammar_errors: int = Field(default=0, ge=0)
    grammar_issues: List[GrammarIssue] = Field(default_factory=list)
    cliche_matches: List[str] = Field(default_factory=list)
    detailed_cliches: List[ClicheMatch] = Field(default_factory=list)
    burstiness_score: float = Field(default=0.0, description="Sentence length standard deviation")
    sentence_lengths: List[int] = Field(default_factory=list)
    em_dash_count: int = Field(default=0, ge=0)
    total_words: int = Field(default=0, ge=0)

    @property
    def is_passing(self) -> bool:
        if self.plagiarism_ratio >= 0.08:
            return False
        if self.critical_grammar_errors > 0:
            return False
        if len(self.cliche_matches) > 0:
            return False
        if self.burstiness_score < 8.5:
            return False
        if self.em_dash_count > 2:
            return False
        return True


class SubPassResult(BaseModel):
    pass_name: str
    pass_key: str
    revised_text: str
    focus: str


class AuditReport(BaseModel):
    iteration: int
    metrics: AuditMetrics
    feedback_summary: str
    flagged_sentences: List[str] = Field(default_factory=list)
    sub_passes: List[SubPassResult] = Field(default_factory=list)
    draft_snapshot: str = ""
    timestamp: str = ""


class ArticleDraft(BaseModel):
    original_bahasa: str
    current_english_draft: str = ""
    iteration_history: List[AuditReport] = Field(default_factory=list)
    sub_pass_history: List[SubPassResult] = Field(default_factory=list)
    status: PipelineStatus = PipelineStatus.INITIALIZING
    error_message: Optional[str] = None


class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Draft text in Bahasa Indonesia")
    max_retries: int = Field(default=3, ge=1, le=5)
    target_tone: str = Field(default="editorial", description="Writing tone")
    api_key: Optional[str] = Field(default=None, description="Optional Gemini API key from frontend")


class ProcessResponse(BaseModel):
    success: bool
    final_draft: ArticleDraft
    processing_time_sec: float
