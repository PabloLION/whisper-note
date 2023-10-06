from enum import Enum
from typing import Any, Optional, Protocol, Union, cast, overload
from parse_env_cfg import TRANSLATE, parsed_config
import deepl


class TranslatorProtocol(Protocol):
    # not saving API key because it's safer and we don't need it later.
    translator: Union[deepl.Translator, Any]  # TODO: Add other translators

    def translate(
        self, text: str, target_lang, source_lang: Optional[Any] = None
    ) -> str:
        ...


class Language(Enum):
    ES = "Spanish"
    EN = "English"
    CN = "Chinese_Simplified"


class DeepLTranslator(TranslatorProtocol):
    translator: deepl.Translator

    def __init__(self, api_key: str):
        self.translator = deepl.Translator(api_key)

    def translate(
        self, text: str, target_lang: Language, source_lang: Optional[Language] = None
    ) -> str:
        result = self.translator.translate_text(
            text,
            source_lang=self.to_deepl_language(source_lang),
            target_lang=self.to_deepl_language(target_lang),
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
        return {
            Language.ES: cast(deepl.Language, deepl.Language.SPANISH),
            Language.EN: cast(deepl.Language, deepl.Language.ENGLISH),
            Language.CN: cast(deepl.Language, deepl.Language.CHINESE),
        }[lang]


def get_translator() -> TranslatorProtocol:
    if TRANSLATE == "deepl":
        return DeepLTranslator(parsed_config["TRANSLATE_API_KEY"])
    else:
        raise ValueError(f"Unknown translator: {TRANSLATE=}")


def test_deepl_translate():
    translator = DeepLTranslator(parsed_config["TRANSLATE_API_KEY"])
    test_translate = translator.translate("Hello, world!", Language.CN, Language.EN)
    assert test_translate == "你好，世界", f"{test_translate=}"


if __name__ == "__main__":
    test_deepl_translate()
