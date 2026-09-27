import os
import re
from typing import Optional, List
import httpx
from infrastructure.heuristic_linter import CLICHE_REPLACEMENTS


class GeminiClient:
    """High-quality translation & humanizing client using Gemini 2.5 Flash with Google Translate engine fallback."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    async def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        if self._client:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction or None,
                    temperature=0.7,
                )
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                if response and response.text and len(response.text.strip()) > 10:
                    return response.text.strip()
            except Exception as e:
                print(f"[Gemini API Notice] {e}. Falling back to clean Google Translate engine.")
        return await self._fallback_translate_or_rewrite(prompt, system_instruction)

    def _clean_prompt_target(self, prompt: str) -> str:
        if '"""' in prompt:
            parts = prompt.split('"""')
            if len(parts) >= 3:
                return parts[1].strip()
            if len(parts) == 2:
                return parts[1].strip() if parts[1].strip() else parts[0].strip()

        prefix = "Please translate this draft into natural English:\n\n"
        if prefix in prompt:
            return prompt.replace(prefix, "").strip()

        return prompt.strip()

    async def _fallback_translate_or_rewrite(self, prompt: str, system_instruction: str) -> str:
        target_text = self._clean_prompt_target(prompt)
        sys_lower = system_instruction.lower()

        # Stage 1: Translation via Google Translate Engine
        if "translate" in sys_lower:
            return await self._translate_google(target_text)

        # Stage 3 Pass 1: Orwell's 6 Rules (lguz)
        if "orwell" in sys_lower:
            return self._apply_orwell_filter(target_text)

        # Stage 3 Pass 2: Rhythm & Syntax Variance (blader)
        if "rhythm" in sys_lower or "burstiness" in sys_lower:
            return self._apply_rhythm_filter(target_text)

        # Stage 3 Pass 3: Specificity (conorbronsdon)
        if "specificity" in sys_lower or "conorbronsdon" in sys_lower:
            return self._apply_specificity_filter(target_text)

        return target_text

    async def _translate_single_block(self, client: httpx.AsyncClient, block: str) -> str:
        if not block.strip():
            return ""
        # Preserve headers or quotes
        prefix = ""
        content = block
        if block.startswith("#"):
            match = re.match(r"^(#+\s*)", block)
            if match:
                prefix = match.group(1)
                content = block[len(prefix):]
        elif block.startswith(">"):
            prefix = "> "
            content = block[1:].strip()

        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {"client": "gtx", "sl": "id", "tl": "en", "dt": "t", "q": content}
            r = await client.get(url, params=params, timeout=10.0)
            if r.status_code == 200:
                data = r.json()
                translated = "".join([part[0] for part in data[0] if part and part[0]])
                return prefix + translated.strip()
        except Exception as e:
            print(f"[Block Translation Fallback] {e}")
        return block

    async def _translate_google(self, text: str) -> str:
        import asyncio
        paragraphs = text.split("\n\n")
        async with httpx.AsyncClient() as client:
            tasks = [self._translate_single_block(client, p) for p in paragraphs]
            translated_blocks = await asyncio.gather(*tasks)
            full_text = "\n\n".join(translated_blocks)
            return self._apply_orwell_filter(full_text)

    def _apply_orwell_filter(self, text: str) -> str:
        """Cut clutter, active voice, and eradicate AI cliches (lguz)."""
        revised = text
        for cliche, replacement in CLICHE_REPLACEMENTS.items():
            first_choice = replacement.split(",")[0].split(" or ")[0].strip()
            pattern = re.compile(rf"\b{re.escape(cliche)}\b", re.IGNORECASE)
            revised = pattern.sub(first_choice, revised)
        
        revised = re.sub(r"\bin order to\b", "to", revised, flags=re.IGNORECASE)
        revised = re.sub(r"\butilize\b", "use", revised, flags=re.IGNORECASE)
        revised = re.sub(r"\bmethodology\b", "method", revised, flags=re.IGNORECASE)
        revised = re.sub(r"\bit is important to note that\b", "note that", revised, flags=re.IGNORECASE)
        return revised

    def _apply_rhythm_filter(self, text: str) -> str:
        """Vary cadence, strip em-dashes, and ensure clean paragraph structure (blader)."""
        # Replace em-dashes with comma or period
        revised = re.sub(r"—| - |--", ", ", text)
        
        # Process each paragraph
        paragraphs = revised.split("\n\n")
        output_paras = []
        for p in paragraphs:
            if not p.strip():
                continue
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
            rhythmic = []
            for s in sentences:
                words = s.split()
                if len(words) > 35 and "," in s:
                    comma_idx = s.find(",")
                    s1 = s[:comma_idx].strip() + "."
                    s2 = s[comma_idx + 1:].strip()
                    s2 = s2[0].upper() + s2[1:] if s2 else ""
                    rhythmic.extend([s1, s2])
                else:
                    rhythmic.append(s)
            output_paras.append(" ".join(rhythmic))

        return "\n\n".join(output_paras)

    def _apply_specificity_filter(self, text: str) -> str:
        """Clean double commas and whitespace while strictly keeping paragraphs (conorbronsdon)."""
        paragraphs = text.split("\n\n")
        cleaned_paras = []
        for p in paragraphs:
            cleaned = re.sub(r",\s*,", ",", p)
            cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
            if cleaned:
                cleaned_paras.append(cleaned)
        return "\n\n".join(cleaned_paras)
