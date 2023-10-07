import dotenv
import os
import yaml

from whisper_note.supportive_class import Language, FrozenConfig


class ConfigLoadingError(ValueError):
    pass


DEFAULT_CONFIG_FOLDER = os.path.abspath(
    os.path.join(os.path.abspath(__file__), "..", "..")
)


def parse_env_and_config(env_config_path: str = DEFAULT_CONFIG_FOLDER) -> FrozenConfig:
    cfg_path = os.path.join(env_config_path, "config.yml")
    env_path = os.path.join(env_config_path, ".env")
    assert os.path.exists(cfg_path), f"config.yml not found in {env_config_path=}"
    assert os.path.exists(env_path), f".env not found in {env_config_path=}"

    parsed_cfg = {}
    dotenv.load_dotenv(os.path.join(env_config_path, ".env"))

    with open(cfg_path) as cfg_file:
        cfg = yaml.safe_load(cfg_file)
        parsed_cfg["dot_env_path"] = os.path.join(env_config_path, ".env")
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
            parsed_cfg["translator_env_key"] = ""
        case "DEEPL":
            parsed_cfg["translator_env_key"] = "DEEPL_API_KEY"
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
