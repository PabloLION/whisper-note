import os
from queue import Queue
import sys
from time import sleep
from typing import cast

import torch
import whisper
from whisper_note.recorder import ChunkedRecorder
from whisper_note.supportive_class import (
    FrozenConfig,
    Language,
    WavTimeSizeQueue,
    get_translator,
)
from whisper_note.transcription import Transcriptions


class Transcriber:
    config: FrozenConfig
    whisper_model: whisper.Whisper
    data_q: WavTimeSizeQueue
    recorder: ChunkedRecorder
    transcription: Transcriptions

    def __init__(self, config: FrozenConfig) -> None:
        self.config = config
        self.whisper_model = self._load_whisper_model()
        self.data_q = Queue()  # thread-safe queue, record audio in background
        self.recorder = ChunkedRecorder(self.data_q, config)
        self.transcription = Transcriptions(
            live_print=True, live_translator=get_translator(self.config)
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

    def live_transcribe(self) -> None:
        print("Recording started...")  # Cue the user to go.
        while True:
            try:  # to not block the keyboard interrupt
                temp_wav, time, size = self.recorder.get_next_part()
                if temp_wav is None:
                    sleep(0.3)  # uninterruptedly recording in another thread
                    continue

                transcribed = self.whisper_model.transcribe(
                    temp_wav.name, fp16=torch.cuda.is_available()
                )  # Get transcription from the whisper.
                text = cast(str, transcribed["text"]).strip()
                if text == "":
                    continue
                self.transcription.add_phrase(time, text, size)
                self.transcription.rich_print(self.recorder.pending_time_size)
            except KeyboardInterrupt:
                break
        # If the loop is broken, we are done recording.
        self._on_stop_recording()

    def _on_stop_recording(self):
        print("Stopping recording...")
        if self.config.store_merged_wav:  # double checking is good
            self.recorder.gen_full_wav()
            for wav in self.recorder.all_wav:
                wav.close()
                print(f"Deleting piece {wav.name}")
                os.remove(wav.name)
        # TODO: Do the export thing.

    def get_transcription(self):
        return self.transcription
