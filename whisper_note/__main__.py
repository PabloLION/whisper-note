from transcribe import real_time_transcribe
from whisper_note.parse_env_cfg import CONFIG


if __name__ == "__main__":
    real_time_transcribe(CONFIG)
    print("Done!")
