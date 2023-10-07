# TODO: ren protocol_translator
import os
from typing import Any, Optional, Protocol, Union
import deepl

from whisper_note.supportive_class import FrozenConfig


class TranslatorProtocol(Protocol):
    # not saving API key because it's safer and we don't need it later.
    translator: Union[deepl.Translator, Any]  # TODO: Add other translators
    config: FrozenConfig

    def __init__(
        self,
        api_key: str,
        config: FrozenConfig,
    ):
        ...

    def get_api_key(self) -> str:
        key = os.getenv(self.config.translator_env_key)
        if key is None:
            raise ValueError("translator api key is not set in .env file")
        return key

    def translate(self, text: str) -> str:
        ...


class DeepLTranslator(TranslatorProtocol):
    translator: deepl.Translator
    config: FrozenConfig

    def __init__(
        self,
        config: FrozenConfig,
    ):
        self.config = config
        self.translator = deepl.Translator(self.get_api_key())

    def translate(self, text: str) -> str:
        if text == "":
            return ""
        target, source = self.config.target_lang, self.config.source_lang
        result = self.translator.translate_text(
            text,
            target_lang=target.to_deepl_language(),
            source_lang=source and source.to_deepl_language(),
        )
        if isinstance(result, list):
            raise ValueError(f"DeepL returned a list of translations: {result=}")
        return result.text


def get_translator(config: FrozenConfig) -> Optional[TranslatorProtocol]:
    return DeepLTranslator(config)
