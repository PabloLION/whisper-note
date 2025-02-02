from pathlib import Path
from typing import NamedTuple, final
from .enum_language import Language


class InvalidConfigError(ValueError):
    pass


# I don't know how to get a data
ConfigValue = str | Language | int | None


@final
class FrozenConfig(NamedTuple):
    dot_env_path: str
    translator: str
    translator_env_key: str
    model: str
    source_lang: Language | None  # both translator and whisper support None
    target_lang: Language
    linux_microphone: str | None
    energy_threshold: int  # TODO: name it better
    phrase_max_second: int
    summarizer: str
    store_merged_wav: Path | None
    merged_transcription: Path | None
    live_history_html: Path | None

    def mutated_copy(self: "FrozenConfig", **kwargs: ConfigValue) -> "FrozenConfig":
        copy = FrozenConfig(**{**self._asdict(), **kwargs})  # type: ignore
        copy.__type_check__()  # do the type check due to type ignore above
        return copy

    def __type_check__(self) -> None:
        expected_type = {
            "dot_env_path": str,
            "translator": str,
            "translator_env_key": str,
            "model": str,
            "source_lang": Language | None,
            "target_lang": Language,
            "linux_microphone": str | None,
            "energy_threshold": int,
            "phrase_max_second": int,
            "summarizer": str,
            "store_merged_wav": Path | None,
            "merged_transcription": Path | None,
            "live_history_html": Path | None,
        }
        for k, v in self._asdict().items():
            if isinstance(v, expected_type[k]):
                continue
            raise InvalidConfigError(f"Invalid config value type: {type(v)} for {k}")


EXAMPLE_CONFIG = FrozenConfig(
    dot_env_path="",
    translator="DEEPL",
    translator_env_key="DEEPL_API_KEY",
    model="small",
    source_lang=Language.EN,
    target_lang=Language.CN,
    linux_microphone=None,
    energy_threshold=805000,
    phrase_max_second=3,
    summarizer="NONE",
    store_merged_wav=None,
    merged_transcription=None,
    live_history_html=None,
)
