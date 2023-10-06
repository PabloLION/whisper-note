from enum import Enum
from typing import Any, Optional, Protocol, Union, cast, overload
from parse_env_cfg import CONFIG
import deepl


class Language(Enum):
    ES = "Spanish"
    EN = "English"
    EN_US = "American_English"
    EN_GB = "British_English"
    CN = "Chinese_Simplified"


class TranslatorProtocol(Protocol):
    # not saving API key because it's safer and we don't need it later.
    translator: Union[deepl.Translator, Any]  # TODO: Add other translators

    def __init__(
        self,
        api_key: str,
        target_lang: Language,
        source_lang: Optional[Language] = None,
    ):
        ...

    def translate(self, text: str) -> str:
        ...


class DeepLTranslator(TranslatorProtocol):
    translator: deepl.Translator

    def __init__(
        self,
        api_key: str,
        target_lang: Language,
        source_lang: Optional[Language] = None,
    ):
        self.translator = deepl.Translator(api_key)
        self.target_lang = target_lang
        self.source_lang = source_lang

    def translate(self, text: str) -> str:
        result = self.translator.translate_text(
            text,
            target_lang=self.to_deepl_language(self.target_lang),
            source_lang=self.to_deepl_language(self.source_lang),
        )
        if isinstance(result, list):
            raise ValueError(f"DeepL returned a list of translations: {result=}")
        return result.text

    @overload
    @staticmethod
    def to_deepl_language(lang: None) -> None:
        ...

    @overload
    @staticmethod
    def to_deepl_language(lang: Language) -> deepl.Language:
        ...

    @staticmethod
    def to_deepl_language(lang: Optional[Language]) -> Optional[deepl.Language]:
        if lang is None:
            return None
        try:
            return {
                Language.ES: cast(deepl.Language, deepl.Language.SPANISH),
                Language.EN: cast(deepl.Language, deepl.Language.ENGLISH),
                Language.EN_US: cast(deepl.Language, deepl.Language.ENGLISH_AMERICAN),
                Language.EN_GB: cast(deepl.Language, deepl.Language.ENGLISH_BRITISH),
                Language.CN: cast(deepl.Language, deepl.Language.CHINESE),
            }[lang]
        except KeyError:
            raise ValueError(f"Unknown language: {lang=}")


def get_translator(
    target_lang: Language, source_lang: Optional[Language] = None
) -> Optional[TranslatorProtocol]:
    if CONFIG.translator == "NONE":
        return None
    if CONFIG.translator == "DEEPL":
        return DeepLTranslator(CONFIG.translator_key, target_lang, source_lang)
    else:
        raise ValueError(f"Unknown translator: {CONFIG.translator=}")


def test_deepl_translate():
    translator = DeepLTranslator(CONFIG.translator_key, Language.CN, Language.EN)
    test_translate = translator.translate("Hello, world")
    assert test_translate == "你好，世界", f"expected '你好，世界', got {test_translate=}"


def test_language():
    assert Language("Spanish") == Language.ES
    assert Language("American_English") == Language.EN_US


if __name__ == "__main__":
    test_language()
    test_deepl_translate()
