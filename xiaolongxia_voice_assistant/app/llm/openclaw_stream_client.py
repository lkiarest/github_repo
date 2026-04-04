import json
import os
from typing import Generator, Any, Dict

import requests


class OpenClawStreamClient:
    def __init__(self):
        self.base_url = os.getenv("OPENCLAW_BASE_URL", "http://127.0.0.1:18789/v1").rstrip("/")
        self.api_key = os.getenv("OPENCLAW_API_KEY", "openclaw-local")
        self.model = os.getenv("OPENCLAW_MODEL", "")
        self.timeout = int(os.getenv("OPENCLAW_TIMEOUT_SECONDS", "90"))

    def stream_chat(
        self,
        text: str,
        system_prompt: str = "你是小龙虾，一个本地语音助手。回答尽量简洁、自然、口语化。",
    ) -> Generator[str, None, None]:
        if not self.model:
            yield "还没有配置 OPENCLAW_MODEL。"
            return

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.4,
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
            timeout=self.timeout,
            stream=True,
        ) as response:
            response.raise_for_status()

            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break

                try:
                    event = json.loads(data)
                except json.JSONDecodeError:
                    continue

                delta = (((event.get("choices") or [{}])[0]).get("delta") or {})
                content = delta.get("content")
                if isinstance(content, str) and content:
                    yield content
