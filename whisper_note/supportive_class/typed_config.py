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
    energy_threshold: int
    phrase_max_second: int
    summarizer: str
    # #TODO: use a path lib Path for my config Path for readability
    store_merged_wav: str
    merged_transcription: str
    live_history_html: str

    def mutated_copy(self: "FrozenConfig", **kwargs: ConfigValue) -> "FrozenConfig":
        nf = FrozenConfig(**{**self._asdict(), **kwargs})  # type: ignore
        nf.__type_check__()  # do the type check due to type ignore above
        return nf

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
            # #TODO: change these three to Path
            "store_merged_wav": str,
            "merged_transcription": str,
            "live_history_html": str,
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
    energy_threshold=1000,
    phrase_max_second=3,
    summarizer="NONE",
    store_merged_wav="",
    merged_transcription="",
    live_history_html="",
)
