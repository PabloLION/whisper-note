from whisper_note.supportive_class import Language


def test_language_enum():
    assert Language("Spanish") == Language.ES
    assert Language.__getitem__("EN") == Language.EN
    assert Language("American_English") == Language.EN_US
