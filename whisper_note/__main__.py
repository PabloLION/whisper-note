from whisper_note.supportive_class.constants import LOG
from whisper_note.transcriber import Transcriber
from whisper_note.parse_env_cfg import CONFIG


def run_core():
    transcriber = Transcriber(CONFIG)
    transcriber.live_transcribe()
    LOG.info("Finished! Exiting gracefully")


def run():
    # hooked to "poetry run whisper-note", "poetry run note".
    run_core()


if __name__ == "__main__":
    run()
