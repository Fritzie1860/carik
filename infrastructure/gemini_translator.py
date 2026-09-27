from infrastructure.gemini_client import GeminiClient


class GeminiTranslator:
    """Translates Indonesian draft into natural English applying conorbronsdon style guide."""

    def __init__(self, client: GeminiClient) -> None:
        self.client = client

    async def translate(self, text: str) -> str:
        system_prompt = (
            "You are an elite editorial translator applying the conorbronsdon style guide:\n"
            "1. Thought-Leadership Tone: Write with sharp, authoritative, and direct prose.\n"
            "2. Specificity Rule: Avoid vague platitudes and generalities. Ground points with concrete mechanisms.\n"
            "3. Active Phrasing: Use strong, direct active verbs. Cut throat-clearing fluff.\n"
            "4. Zero AI-isms: Strictly ban cliché AI words: delve, tapestry, testament, beacon, pivotal, multifaceted, foster, unlock, seamlessly, furthermore, moreover, in conclusion, vibrant, landscape, harnessing, paradigm, game-changer.\n"
            "5. Preserve all original numbers, facts, technical terminologies, and structure.\n\n"
            "Translate the following Bahasa Indonesia text into natural English draft:"
        )
        user_prompt = f"Please translate this draft into natural English:\n\n{text}"
        return await self.client.generate_text(user_prompt, system_instruction=system_prompt)
