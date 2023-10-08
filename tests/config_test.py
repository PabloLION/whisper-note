from whisper_note.supportive_class import EXAMPLE_CONFIG


def test_config():
    config = EXAMPLE_CONFIG.mutated_copy(translator="DEEPL", model="small")
    assert config.translator == "DEEPL"
    assert config.model == "small"
    config = config.mutated_copy(model="large")
    assert config.model == "large"
