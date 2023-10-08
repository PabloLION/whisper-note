import os
from pathlib import Path
from queue import Queue
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
    LOG,
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
        LOG.info(f"Loading whisper model [{model}]")
        whisper_model = whisper.load_model(model)
        LOG.info(f"Whisper model [{model}] loaded.")
        return whisper_model

    def live_transcribe(self) -> None:
        LOG.info("Recording started...")  # Cue the user to go.
        while True:
            try:  # to not block the keyboard interrupt
                temp_wav, time, size = self.recorder.get_next_part()
                if temp_wav is None:
                    sleep(0.3)  # uninterruptedly recording in another thread
                    continue
                text = self._transcribe_wav(Path(temp_wav.name))
                if text == "":
                    continue
                self.transcription.add_phrase(time, text, size)
                self.transcription.rich_print(self.recorder.pending_time_size)
            except KeyboardInterrupt:
                break
        # If the loop is broken, we are done recording.
        self._on_stop_recording()

    def _transcribe_wav(self, path: Path) -> str:
        transcribed = self.whisper_model.transcribe(
            str(path), fp16=torch.cuda.is_available()
        )  # Get transcription from the whisper.
        return cast(str, transcribed["text"]).strip()

    def _on_stop_recording(self):
        if self.config.store_merged_wav:  # double checking is good
            LOG.info("Stopping recording...")
            self.recorder.write_merged_wav()
            for wav in self.recorder.all_wav:
                wav.close()
                LOG.debug(f"Deleting piece {wav.name}")
                os.remove(wav.name)
            LOG.info(f"Merged wav generated: {self.config.merged_transcription}")

        if self.config.merged_transcription:
            assert self.config.store_merged_wav is not None, "Uncaught invalid config"
            LOG.info("generating transcription...")
            txt = self._transcribe_wav(self.config.store_merged_wav)
            if txt == "":
                LOG.info("No transcription generated. Discarding merged transcription.")
            else:
                with open(self.config.merged_transcription, "w") as f:
                    f.write(txt)
            LOG.info(f"Merged text generated: {self.config.merged_transcription}")

        if self.config.live_history_html:
            LOG.info("generating HTML of live transcription history...")
            self.transcription.export_history_html(self.config.live_history_html)
            LOG.info(
                f"HTML of live transcription history generated: {self.config.live_history_html}"
            )

    def get_transcription(self):
        return self.transcription
