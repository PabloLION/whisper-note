from whisper_note.transcriber import Transcriber
from whisper_note.parse_env_cfg import CONFIG


def run():
    transcriber = Transcriber(CONFIG)
    transcriber.real_time_transcribe()
    print("Done!")


if __name__ == "__main__":
    run()
