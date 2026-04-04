from typing import Iterable


DEFAULT_INTERRUPT_PHRASES = [
    "停一下",
    "等等",
    "先别说",
    "不用说了",
    "闭嘴",
    "暂停",
    "打住",
    "停止",
    "先停",
]


class InterruptIntentMatcher:
    def __init__(self, phrases: Iterable[str] | None = None):
        values = list(DEFAULT_INTERRUPT_PHRASES)
        if phrases:
            values.extend([p for p in phrases if p])
        self.phrases = sorted(set(values), key=len, reverse=True)

    def is_interrupt(self, text: str) -> bool:
        normalized = self._normalize(text)
        return any(self._normalize(phrase) in normalized for phrase in self.phrases)

    def _normalize(self, text: str) -> str:
        return (
            text.strip()
            .replace("，", "")
            .replace("。", "")
            .replace("？", "")
            .replace("！", "")
            .replace(",", "")
            .replace(".", "")
            .replace("?", "")
            .replace("!", "")
            .replace(" ", "")
            .lower()
        )
