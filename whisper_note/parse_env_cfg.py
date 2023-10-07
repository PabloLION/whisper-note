from typing import NamedTuple
import dotenv
import os
import yaml

from whisper_note.supportive_class.language import Language


class ConfigLoadingError(ValueError):
    pass


class FrozenConfig(NamedTuple):
    translator: str
    translator_key: str
    model: str
    source_lang: Language
    target_lang: Language


def parse_env_and_config() -> FrozenConfig:
    dotenv.load_dotenv()  # #TODO: use dynamic env vars for test
    cfg_path = os.path.abspath(__file__ + "/../../config.yml")
    parsed_cfg = {}

    with open(cfg_path) as cfg_file:
        cfg = yaml.safe_load(cfg_file)
        parsed_cfg["model"] = cfg.get("model", "small")
        parsed_cfg["translator"] = cfg.get("translator", "NONE")
        parsed_cfg["source_lang"] = Language(cfg.get("source_lang", "English"))
        parsed_cfg["target_lang"] = Language(
            cfg.get("target_lang", "Chinese_Simplified")
        )

    # parse translator api key
    # match parsed_cfg["translator"] : # #TODO: use this for python 3.10+
    if parsed_cfg["translator"] == "NONE":
        parsed_cfg["translator_key"] = ""
    if parsed_cfg["translator"] == "DEEPL":
        key = os.getenv("DEEPL_API_KEY")
        if not key:
            raise ConfigLoadingError("DEEPL_API_KEY is not set in .env file")
        parsed_cfg["translator_key"] = key
    else:
        raise ConfigLoadingError(f"Unknown translator: {parsed_cfg['translator'] =}")
    CONFIG = FrozenConfig(**parsed_cfg)
    parsed_cfg.clear()
    return CONFIG


CONFIG = parse_env_and_config()


def test_parse_env_and_config():
    assert CONFIG.translator == "DEEPL", f"expected DEEPL, got {CONFIG.translator=}"
    assert CONFIG.model == "small"


from icecream import ic

ic(CONFIG)
if __name__ == "__main__":
    test_parse_env_and_config()
