from queue import Queue
from time import sleep
from typing import cast

import torch
import whisper
from recorder import ChunkedRecorder
from transcription import Transcriptions
from whisper_note.supportive_class import (
    FrozenConfig,
    Language,
    TimedSampleQueue,
    get_translator,
)


class Transcriber:
    config: FrozenConfig
    whisper_model: whisper.Whisper
    data_q: TimedSampleQueue
    recorder: ChunkedRecorder
    transcription: Transcriptions

    def __init__(self, config: FrozenConfig) -> None:
        self.config = config
        self.whisper_model = self._load_whisper_model()
        self.data_q = Queue()  # thread-safe queue, record audio in background
        self.recorder = ChunkedRecorder(self.data_q, config)
        self.transcription = Transcriptions(
            spontaneous_print=True, spontaneous_translator=get_translator(self.config)
        )  # output transcription

    def _load_whisper_model(self) -> whisper.Whisper:
        """Load / Download whisper model."""
        model = self.config.model
        if self.config.source_lang == Language.EN and not model.endswith(".en"):
            model += ".en"
        print(f"Loading whisper model '{model}'")
        whisper_model = whisper.load_model(model)
        print("Whisper model loaded.")
        return whisper_model

    def real_time_transcribe(self) -> None:
        print("Recording started...")  # Cue the user to go.
        while True:
            try:  # to not block the keyboard interrupt
                time, temp_wav = self.recorder.get_next_part()
                if temp_wav is None:
                    sleep(0.3)  # uninterruptedly recording in another thread
                    continue

                transcribed = self.whisper_model.transcribe(
                    temp_wav.name, fp16=torch.cuda.is_available()
                )  # Get transcription from the whisper.
                text = cast(str, transcribed["text"]).strip()
                self.transcription.add_phrase(time, text)

                self.transcription.print_all(clean=True)
            except KeyboardInterrupt:
                break
        print("Stopping recording...")

    def get_transcription(self):
        return self.transcription
