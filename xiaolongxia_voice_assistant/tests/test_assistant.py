from app.runtime.assistant import Assistant


class DummyQQBot:
    def __init__(self):
        self.sent = []

    def send_message(self, content: str):
        self.sent.append(content)
        return {"mock": True, "content": content}


def test_handle_text_routes_to_qq_for_qq_message():
    assistant = Assistant()
    assistant.qq = DummyQQBot()

    result = assistant.handle_text("给我的QQ发消息：我到家了")

    assert result["status"] == "sent"
    assert result["content"] == "我到家了"
    assert assistant.qq.sent == ["我到家了"]


def test_handle_text_returns_plain_reply_for_normal_text():
    assistant = Assistant()
    assistant.qq = DummyQQBot()

    result = assistant.handle_text("今天天气怎么样")

    assert result == {"reply": "你说的是: 今天天气怎么样"}
    assert assistant.qq.sent == []


def test_send_qq_strips_prefix_and_punctuation():
    assistant = Assistant()
    assistant.qq = DummyQQBot()

    result = assistant.send_qq("给我的QQ发消息：测试一下")

    assert result["content"] == "测试一下"
    assert assistant.qq.sent == ["测试一下"]
