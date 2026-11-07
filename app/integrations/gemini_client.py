import json
import re
from typing import Dict, Any, Optional
import requests
from config.settings import settings

class GeminiClient:
    """Client for Google Gemini API for biomedical literature analysis and synthesis."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-2.5-flash"
        self._sdk_client = None

        if self.api_key:
            try:
                from google import genai
                self._sdk_client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[GeminiClient] Could not initialize google.genai SDK client: {e}")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def analyze_text(self, system_prompt: str, user_content: str, temperature: float = 0.2) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("Gemini API key is not configured. Please set it in Settings.")

        if self._sdk_client:
            try:
                response = self._sdk_client.models.generate_content(
                    model=self.model,
                    contents=f"{system_prompt}\n\n---\nDOCUMENT CONTENT TO ANALYSE:\n{user_content}"
                )
                text = response.text or ""
                return self._clean_and_parse_json(text)
            except Exception as e:
                print(f"[GeminiClient.sdk] Error: {e}, falling back to REST endpoint...")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n---\nDOCUMENT CONTENT TO ANALYSE:\n{user_content}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json"
            }
        }

        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned empty candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        return self._clean_and_parse_json(text)

    def _clean_and_parse_json(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
