import os
import requests
from typing import Any, Dict, List


class OpenClawClient:
    def __init__(self):
        self.base_url = os.getenv("OPENCLAW_BASE_URL", "http://127.0.0.1:18789/v1").rstrip("/")
        self.api_key = os.getenv("OPENCLAW_API_KEY", "openclaw-local")
        self.model = os.getenv("OPENCLAW_MODEL", "")
        self.timeout = int(os.getenv("OPENCLAW_TIMEOUT_SECONDS", "90"))

    def chat(self, text: str, system_prompt: str = "你是小龙虾，一个本地语音助手。回答尽量简洁、自然、口语化。") -> str:
        if not self.model:
            return "还没有配置 OPENCLAW_MODEL。"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.4,
            "stream": False,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        choices: List[Dict[str, Any]] = data.get("choices", [])
        if not choices:
            return "OpenClaw 没有返回可用回复。"

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return "\n".join(part for part in text_parts if part).strip()

        return str(content).strip()
