import time


class ContinuousConversationMode:
    def __init__(self, timeout_seconds: int = 12):
        self.timeout_seconds = timeout_seconds
        self.expires_at = 0.0

    def activate(self):
        self.expires_at = time.time() + self.timeout_seconds

    def touch(self):
        self.expires_at = time.time() + self.timeout_seconds

    def is_active(self) -> bool:
        return time.time() < self.expires_at

    def remaining_seconds(self) -> int:
        remaining = int(self.expires_at - time.time())
        return remaining if remaining > 0 else 0

    def deactivate(self):
        self.expires_at = 0.0
