from whisper_note.supportive_class import Language, DEFAULT_CONFIG, DeepLTranslator


def test_deepl_translate():
    config = DEFAULT_CONFIG.mutated_copy(
        target_lang=Language.CN, source_lang=Language.EN
    )
    translator = DeepLTranslator(config)
    test_translate = translator.translate("Hello, world")
    assert test_translate == "你好，世界", f"expected '你好，世界', got {test_translate=}"

    config = DEFAULT_CONFIG.mutated_copy(target_lang=Language.CN, source_lang=None)
    translator = DeepLTranslator(config)
    test_translate = translator.translate("お名前をいただけますか？")
    assert test_translate == "请问你叫什么名字？", f"expected '请问你叫什么名字？', got {test_translate=}"
