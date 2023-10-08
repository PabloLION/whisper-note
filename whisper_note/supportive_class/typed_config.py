from typing import NamedTuple, final
from .enum_language import Language

# I don't know how to gather the types of values dynamically
ConfigValue = str | Language | int | None


@final
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

    def mutated_copy(self: "FrozenConfig", **kwargs: ConfigValue) -> "FrozenConfig":
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
