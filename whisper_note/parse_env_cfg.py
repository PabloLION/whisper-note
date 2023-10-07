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
    linux_microphone: str | None
    energy_threshold: int
    phrase_max_second: int


DEFAULT_CONFIG_FOLDER = os.path.abspath(
    os.path.join(os.path.abspath(__file__), "..", "..")
)


def parse_env_and_config(env_config_path: str = DEFAULT_CONFIG_FOLDER) -> FrozenConfig:
    dotenv.load_dotenv(os.path.join(env_config_path, ".env"))
    cfg_path = os.path.join(env_config_path, "config.yml")
    parsed_cfg = {}

    with open(cfg_path) as cfg_file:
        cfg = yaml.safe_load(cfg_file)
        parsed_cfg["model"] = cfg.get("model", "small")
        parsed_cfg["translator"] = cfg.get("translator", "NONE")
        parsed_cfg["source_lang"] = Language(cfg.get("source_lang", "English"))
        parsed_cfg["target_lang"] = Language(
            cfg.get("target_lang", "Chinese_Simplified")
        )
        parsed_cfg["linux_microphone"] = cfg.get("linux_microphone", None)
        parsed_cfg["energy_threshold"] = cfg.get("energy_threshold", 1000)
        parsed_cfg["phrase_max_second"] = cfg.get("phrase_max_second", 3)

    # parse translator api key
    match parsed_cfg["translator"]:
        case "NONE":
            parsed_cfg["translator_key"] = ""
        case "DEEPL":
            key = os.getenv("DEEPL_API_KEY")
            if not key:
                raise ConfigLoadingError("DEEPL_API_KEY is not set in .env file")
            parsed_cfg["translator_key"] = key
        case not_matched:
            raise ConfigLoadingError(f"Unknown translator: translator={not_matched}")
    CONFIG = FrozenConfig(**parsed_cfg)
    parsed_cfg.clear()
    return CONFIG


CONFIG = parse_env_and_config()


def test_parse_env_and_config():
    assert CONFIG.translator == "DEEPL", f"expected DEEPL, got {CONFIG.translator=}"
    assert CONFIG.model == "small"


if __name__ == "__main__":
    test_parse_env_and_config()
