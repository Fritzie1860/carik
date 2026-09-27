from domain.models import SubPassResult
from infrastructure.gemini_client import GeminiClient


class OrwellHumanizer:
    """Executes Stage 3 Multi-Pass Paraphrase across Orwell (lguz), Rhythm (blader), and Specificity (conorbronsdon)."""

    def __init__(self, client: GeminiClient) -> None:
        self.client = client

    async def run_pass_1_orwell(self, text: str, feedback: str) -> SubPassResult:
        """Pass 1: Orwell's 6 Rules (lguz)."""
        sys_prompt = (
            "You are an editor enforcing George Orwell's 6 Rules for Writing:\n"
            "1. Never use a metaphor, simile, or figure of speech you are used to seeing in print.\n"
            "2. Never use a long word where a short one will do.\n"
            "3. If it is possible to cut a word out, ALWAYS cut it out.\n"
            "4. Never use the passive voice where you can use the active.\n"
            "5. Never use a foreign phrase, scientific word, or jargon word if you can think of an everyday English equivalent.\n"
            "6. Strip all banned AI clichés: delve, tapestry, testament, beacon, pivotal, multifaceted, foster, unlock, seamlessly, furthermore, moreover, in conclusion.\n"
            "Rewrite the draft strictly following Orwell's rules. Return only the revised text."
        )
        user_prompt = f"Failed Audit Feedback:\n{feedback}\n\nDraft:\n\"\"\"\n{text}\n\"\"\""
        revised = await self.client.generate_text(user_prompt, system_instruction=sys_prompt)
        return SubPassResult(
            pass_name="Pass 1: Orwell's 6 Rules (lguz)",
            pass_key="orwell_pass_1",
            revised_text=revised if revised.strip() else text,
            focus="Clutter reduction, active voice, and cliché eradication."
        )

    async def run_pass_2_rhythm(self, text: str, feedback: str) -> SubPassResult:
        """Pass 2: Rhythm & Syntax Variance (blader)."""
        sys_prompt = (
            "You are a master of prose cadence and rhythm variance (blader/humanizer rule):\n"
            "1. Inject burstiness: vary sentence lengths dramatically. Mix punchy 3-to-6 word sentences with longer, multi-clause rhythmic sentences (burstiness standard deviation MUST be >= 8.5).\n"
            "2. Ban monotonous 15-20 word sentence strings.\n"
            "3. Strip artificial em-dashes (—). Maximum 1 em-dash allowed.\n"
            "4. Do NOT alter facts or delete key arguments.\n"
            "Restructure the sentence rhythm and syntax. Return only the revised text."
        )
        user_prompt = f"Draft to vary rhythm:\n\"\"\"\n{text}\n\"\"\""
        revised = await self.client.generate_text(user_prompt, system_instruction=sys_prompt)
        return SubPassResult(
            pass_name="Pass 2: Rhythm & Syntax Variance (blader)",
            pass_key="rhythm_pass_2",
            revised_text=revised if revised.strip() else text,
            focus="Cadence variation (burstiness σ >= 8.5) and em-dash removal."
        )

    async def run_pass_3_specificity(self, text: str, original_draft: str, feedback: str) -> SubPassResult:
        """Pass 3: Concrete details & anti-generalization (conorbronsdon)."""
        sys_prompt = (
            "You are an editor enforcing the conorbronsdon thought-leadership writing standard:\n"
            "1. Anti-Generalization: Eradicate vague generalities. Ground every argument with clear, concrete mechanisms.\n"
            "2. Specificity: Keep real-world context sharp, technical facts precise, and logic airtight.\n"
            "3. Semantic Preservation: Check against the original text to ensure no metrics, data, or thesis points were lost.\n"
            "Polish the draft with high specificity and thought leadership tone. Return only the revised text."
        )
        user_prompt = f"Current Draft:\n\"\"\"\n{text}\n\"\"\"\n\nOriginal Text:\n\"\"\"\n{original_draft}\n\"\"\""
        revised = await self.client.generate_text(user_prompt, system_instruction=sys_prompt)
        return SubPassResult(
            pass_name="Pass 3: Concrete Details & Anti-Generalization (conorbronsdon)",
            pass_key="specificity_pass_3",
            revised_text=revised if revised.strip() else text,
            focus="Thought leadership depth, factual preservation, and concrete details."
        )
