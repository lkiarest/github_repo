from typing import Iterable


DEFAULT_WAKE_VARIANTS = [
    "小龙虾",
    "小龙下",
    "小龙夏",
    "小龙霞",
    "小聋虾",
    "晓龙虾",
    "晓龙下",
]


class WakeWordMatcher:
    def __init__(self, wake_word: str = "小龙虾", extra_variants: Iterable[str] | None = None):
        variants = {wake_word}
        variants.update(DEFAULT_WAKE_VARIANTS)
        if extra_variants:
            variants.update(v for v in extra_variants if v)
        self.variants = sorted(variants, key=len, reverse=True)
        self.primary_wake_word = wake_word

    def contains_wake_word(self, text: str) -> bool:
        normalized = self._normalize(text)
        return any(self._normalize(variant) in normalized for variant in self.variants)

    def strip_wake_word(self, text: str) -> str:
        cleaned = text.strip()
        for variant in self.variants:
            cleaned = cleaned.replace(variant, "")
        return cleaned.strip(" ，。,:：!！?？")

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
