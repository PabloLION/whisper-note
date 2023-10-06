from collections import namedtuple
import dotenv
import os
import yaml


class ConfigLoadingError(ValueError):
    pass


dotenv.load_dotenv()  # #TODO: use dynamic env vars for test
cfg_path = os.path.abspath(__file__ + "/../../config.yml")
parsed_cfg = {}

with open(cfg_path) as cfg_file:
    cfg = yaml.safe_load(cfg_file)
    parsed_cfg["model"] = cfg["model"] or "small"
    parsed_cfg["translator"] = cfg["translator"] or "NONE"


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

FrozenConfig = namedtuple("ImmutableDict", ["translator", "translator_key", "model"])
CONFIG = FrozenConfig(**parsed_cfg)
parsed_cfg.clear()


def test_parse_env_and_config():
    assert CONFIG.translator == "DEEPL", f"expected DEEPL, got {CONFIG.translator=}"
    assert CONFIG.model == "large"


if __name__ == "__main__":
    test_parse_env_and_config()
