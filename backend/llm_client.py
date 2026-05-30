import httpx
import json

from .config import settings


class LLMClient:
    def __init__(self):
        self.llm_model = settings.llm_model or "mistral"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.httpx_timeout = 60

    async def complete(self, prompt: str) -> str:
        # Use Ollama local API
        payload = {
            "model": self.llm_model,
            "prompt": f"You are an expert travel planner and itinerary designer.\n\n{prompt}",
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.httpx_timeout) as client:
                response = await client.post(self.ollama_url, json=payload)
                if response.status_code != 200:
                    import logging
                    logging.error(f"Ollama Error: {response.status_code} - {response.text}")
                response.raise_for_status()
                data = response.json()
            return data.get("response", "")
        except Exception as e:
            import logging
            logging.error(f"LLM Error: {str(e)}")
            return ""
