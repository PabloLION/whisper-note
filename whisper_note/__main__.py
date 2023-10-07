from whisper_note.transcriber import Transcriber
from whisper_note.parse_env_cfg import CONFIG
from whisper_note.tui import run_textual_ui


def run_tui():
    run_textual_ui()


def run_core():
    transcriber = Transcriber(CONFIG)
    transcriber.real_time_transcribe()
    print("Done!")


def run():
    # hooked to poetry run whisper-note, poetry run note
    run_tui()


if __name__ == "__main__":
    run_textual_ui()
