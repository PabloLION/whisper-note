from enum import Enum
from typing import Any, Optional, Protocol, Union, cast, overload
from parse_env_cfg import CONFIG
import deepl

from whisper_note.supportive_class.language import Language


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
        if text == "":
            return ""
        result = self.translator.translate_text(
            text,
            target_lang=self.target_lang.to_deepl_language(),
            source_lang=self.source_lang and self.source_lang.to_deepl_language(),
        )
        if isinstance(result, list):
            raise ValueError(f"DeepL returned a list of translations: {result=}")
        return result.text


def get_translator() -> Optional[TranslatorProtocol]:
    if CONFIG.translator == "NONE":
        return None
    if CONFIG.translator == "DEEPL":
        return DeepLTranslator(
            CONFIG.translator_key, CONFIG.target_lang, CONFIG.source_lang
        )
    else:
        raise ValueError(f"Unknown translator: {CONFIG.translator=}")


def test_deepl_translate():
    translator = DeepLTranslator(CONFIG.translator_key, Language.CN, Language.EN)
    test_translate = translator.translate("Hello, world")
    assert test_translate == "你好，世界", f"expected '你好，世界', got {test_translate=}"

    translator = DeepLTranslator(CONFIG.translator_key, Language.CN, None)
    test_translate = translator.translate("お名前をいただけますか？")
    assert test_translate == "请问你叫什么名字？", f"expected '请问你叫什么名字？', got {test_translate=}"


if __name__ == "__main__":
    test_deepl_translate()
