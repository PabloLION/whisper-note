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


def load_whisper_model(config: FrozenConfig) -> whisper.Whisper:
    """Load / Download whisper model."""
    model = config.model
    if config.source_lang == Language.EN and not model.endswith(".en"):
        model += ".en"
    print(f"Loading whisper model '{model}'")
    return whisper.load_model(model)


def real_time_transcribe(config) -> Transcriptions:
    # background thread to record audio data
    data_queue: TimedSampleQueue = Queue()  # thread-safe, store data from recording

    # output transcription
    transcription = Transcriptions(
        spontaneous_print=True, spontaneous_translator=get_translator(config)
    )

    whisper_model: whisper.Whisper = load_whisper_model(config)
    print("Model loaded. Recording...")  # Cue the user that we're ready to go.

    recorder = ChunkedRecorder(data_queue, config)

    while True:
        try:  # to not block the keyboard interrupt
            time, temp_wav = recorder.get_next_part()
            if temp_wav is None:
                sleep(0.3)  # uninterruptedly recording in another thread
                continue

            # Get transcription from the model.
            transcribed = whisper_model.transcribe(
                temp_wav.name, fp16=torch.cuda.is_available()
            )
            text = cast(str, transcribed["text"]).strip()

            # Append new transcription text to transcription.
            transcription.new_phrase(time, text)
            transcription.print_all(clean=True)

        except KeyboardInterrupt:
            break

    transcription.print_all()
    print("Stopping recording...")

    return transcription
