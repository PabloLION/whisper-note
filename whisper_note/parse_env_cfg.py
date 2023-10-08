from datetime import datetime
import dotenv
import os
import yaml

from whisper_note.supportive_class import (
    Language,
    FrozenConfig,
    InvalidConfigError,
    format_filename,
)


DEFAULT_CONFIG_FOLDER = os.path.abspath(os.path.join(__file__, "..", ".."))


def assert_empty_file(path: str, config_name: str) -> None:
    if not path:
        return

    if not os.path.exists(path):
        ...  # The creation is automatic when opened in "ab" mode.
    elif os.path.isdir(path):  # #TODO:TBD gen a .wav file in this folder?
        raise InvalidConfigError(f"config {config_name}={path} is a directory")
    elif os.path.getsize(path) != 0:
        raise InvalidConfigError(f"config {config_name}={path} is not empty")


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
        parsed_cfg["store_merged_wav"] = cfg.get("store_merged_wav", False)
        parsed_cfg["summarizer"] = cfg.get("summarizer", "NONE")
        parsed_cfg["merged_transcription"] = cfg.get("merged_transcription", False)

    # parse translator api key
    match parsed_cfg["translator"]:
        case "NONE":
            parsed_cfg["translator_env_key"] = ""
        case "DEEPL":
            parsed_cfg["translator_env_key"] = "DEEPL_API_KEY"
        case not_matched:
            raise InvalidConfigError(f"Unknown translator: translator={not_matched}")

    # check the merged wav file
    wav_path = parsed_cfg["store_merged_wav"]
    if wav_path == "[LIVE]":
        filename = format_filename(f"{datetime.now()}.wav")
        parsed_cfg["store_merged_wav"] = wav_path = filename
    assert_empty_file(wav_path, "store_merged_wav")
    if wav_path == "" and parsed_cfg["merged_transcription"]:
        raise InvalidConfigError(
            "merged_transcription is only available when store_merged_wav is not empty"
        )

    # merged transcription
    txt_path = parsed_cfg["merged_transcription"]
    if txt_path == "[LIVE]":
        filename = format_filename(f"{datetime.now()}.txt")
        parsed_cfg["merged_transcription"] = txt_path = filename
    assert_empty_file(txt_path, "merged_transcription")
    if txt_path == "" and parsed_cfg["summarizer"] != "NONE":
        raise InvalidConfigError(
            "summarizer is only available when merged_transcription is not empty"
        )

    # parse summarizer
    if parsed_cfg["summarizer"] == "NONE":
        ...  # Do nothing
    elif parsed_cfg["summarizer"] == "GPT3":
        parsed_cfg["summarizer_env_key"] = "GPT3_API_KEY"
    else:
        raise InvalidConfigError(
            f"Unknown summarizer: summarizer={parsed_cfg['summarizer']}"
        )

    CONFIG = FrozenConfig(**parsed_cfg)
    parsed_cfg.clear()
    return CONFIG


CONFIG = parse_env_and_config()
