import json
import os
from typing import Generator, Any, Dict, List

import requests


class OpenClawStreamClientV2:
    def __init__(self):
        self.base_url = os.getenv("OPENCLAW_BASE_URL", "http://127.0.0.1:18789/v1").rstrip("/")
        self.api_key = os.getenv("OPENCLAW_API_KEY", "openclaw-local")
        self.model = os.getenv("OPENCLAW_MODEL", "")

    def stream_chat(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        with requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers,
            stream=True,
        ) as response:
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                except:
                    continue

                delta = (((event.get("choices") or [{}])[0]).get("delta") or {})
                content = delta.get("content")
                if content:
                    yield content
