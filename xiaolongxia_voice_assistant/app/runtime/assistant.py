from app.integrations.qq_bot import QQBot

class Assistant:
    def __init__(self):
        self.qq = QQBot()

    def handle_text(self, text: str):
        if "QQ" in text or "qq" in text:
            return self.send_qq(text)
        return {"reply": f"你说的是: {text}"}

    def send_qq(self, text: str):
        content = text.replace("给我的QQ发消息", "").strip("：: ")
        result = self.qq.send_message(content)
        return {"status": "sent", "content": content, "qq_result": result}
