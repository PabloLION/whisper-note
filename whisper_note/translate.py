from enum import Enum
from typing import Any, Optional, Protocol, Union, cast, overload
from parse_env_cfg import TRANSLATE, parsed_config
import deepl


class TranslatorProtocol(Protocol):
    # not saving API key because it's safer and we don't need it later.
    translator: Union[deepl.Translator, Any]  # TODO: Add other translators

    def translate(self, text: str, target_lang, origin_lang) -> str:
        ...


class Lang(Enum):
    ES = "Spanish"
    EN = "English"
    CN = "Chinese_Simplified"


class DeepLTranslator(TranslatorProtocol):
    translator: deepl.Translator

    def __init__(self, api_key: str):
        self.translator = deepl.Translator(api_key)

    def translate(
        self, text: str, target_lang: Lang, source_lang: Optional[Lang] = None
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
    def to_deepl_language(lang: Lang) -> deepl.Language:
        ...

    @staticmethod
    def to_deepl_language(lang: Optional[Lang]) -> Optional[deepl.Language]:
        if lang is None:
            return None
        return {
            Lang.ES: cast(deepl.Language, deepl.Language.SPANISH),
            Lang.EN: cast(deepl.Language, deepl.Language.ENGLISH),
            Lang.CN: cast(deepl.Language, deepl.Language.CHINESE),
        }[lang]


def test_deepl_translate():
    translator = DeepLTranslator(parsed_config["TRANSLATE_API_KEY"])
    test_translate = translator.translate("Hello, world!", Lang.CN, Lang.EN)
    assert test_translate == "你好，世界", f"{test_translate=}"


if __name__ == "__main__":
    test_deepl_translate()
