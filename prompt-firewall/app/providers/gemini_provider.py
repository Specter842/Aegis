import os
import httpx
from typing import Any, Dict, List
from app.providers.base import BaseProvider, ProviderException

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None, timeout_sec: int = 30):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.timeout_sec = timeout_sec
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        if not self.api_key:
            raise ProviderException("auth_failure", "Gemini API key not configured")

        use_model = model or self.model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{use_model}:generateContent?key={self.api_key}"

        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        try:
            async with httpx.AsyncClient(timeout=self.timeout_sec) as client:
                response = await client.post(url, json={"contents": contents})

                if response.status_code in (401, 403):
                    raise ProviderException("auth_failure", "Invalid Gemini API Key")
                elif 400 <= response.status_code < 500:
                    raise ProviderException("upstream_4xx", f"Gemini Error: {response.text}")
                elif response.status_code >= 500:
                    raise ProviderException("upstream_5xx", f"Gemini Server Error: {response.text}")

                data = response.json()
                try:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    raise ProviderException("malformed_response", "Gemini returned unexpected structure")

                return {"role": "assistant", "content": text}

        except httpx.TimeoutException:
            raise ProviderException("timeout", f"Gemini timed out after {self.timeout_sec}s")
        except httpx.RequestError as e:
            raise ProviderException("network_error", f"Gemini network error: {str(e)}")
        except Exception as e:
            if isinstance(e, ProviderException):
                raise e
            raise ProviderException("unknown_error", str(e))
