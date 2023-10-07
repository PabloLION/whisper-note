from transcribe import Transcriber
from whisper_note.parse_env_cfg import CONFIG


if __name__ == "__main__":
    transcriber = Transcriber(CONFIG)
    transcriber.real_time_transcribe()
    print("Done!")
