import json
from app.llm.openclaw_client import OpenClawClient


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def test_openclaw_parses_simple_text_response(monkeypatch):
    client = OpenClawClient()
    client.model = "test-model"

    def fake_post(*args, **kwargs):
        return DummyResponse({
            "choices": [
                {"message": {"content": "你好"}}
            ]
        })

    monkeypatch.setattr("requests.post", fake_post)

    result = client.chat("hello")

    assert result == "你好"


def test_openclaw_handles_missing_choices(monkeypatch):
    client = OpenClawClient()
    client.model = "test-model"

    def fake_post(*args, **kwargs):
        return DummyResponse({})

    monkeypatch.setattr("requests.post", fake_post)

    result = client.chat("hello")

    assert "没有返回" in result
