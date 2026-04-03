import os

class QQBot:
    def __init__(self):
        self.appid = os.getenv("QQ_BOT_APPID")
        self.token = os.getenv("QQ_BOT_TOKEN")

    def send_message(self, content: str):
        if not self.token:
            return {"error": "QQ token not configured"}

        # TODO: replace with real QQ bot API call
        return {
            "mock": True,
            "content": content
        }
