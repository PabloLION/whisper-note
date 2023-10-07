from typing import NamedTuple
from .enum_language import Language


class FrozenConfig(NamedTuple):
    dot_env_path: str
    translator: str
    translator_env_key: str
    model: str
    source_lang: Language
    target_lang: Language
    linux_microphone: str | None
    energy_threshold: int
    phrase_max_second: int

    def mutated_copy(
        self: "FrozenConfig", **kwargs: str | Language | None | int
    ) -> "FrozenConfig":
        return FrozenConfig(**{**self._asdict(), **kwargs})


DEFAULT_CONFIG = FrozenConfig(
    dot_env_path="",
    translator="DEEPL",
    translator_env_key="DEEPL_API_KEY",
    model="small",
    source_lang=Language.EN,
    target_lang=Language.CN,
    linux_microphone=None,
    energy_threshold=1000,
    phrase_max_second=3,
)
