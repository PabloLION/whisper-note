import io
from datetime import datetime, timedelta
from queue import Queue
from sys import platform
from tempfile import _TemporaryFileWrapper, NamedTemporaryFile
from time import sleep
from typing import cast

import speech_recognition as sr
import torch
import whisper
from result import Err, Ok, Result

from transcription import Transcriptions
from whisper_note.parse_env_cfg import CONFIG
from whisper_note.supportive_class import get_translator, Language

TimedSampleQueue = Queue[tuple[datetime, bytes]]


def load_microphone_source() -> Result[sr.Microphone, str]:
    if "linux" not in platform:
        source = sr.Microphone(sample_rate=16000)
        return Ok(source)

    # only Linux users need this to prevent permanent application hang / crash
    mic_name = CONFIG.linux_microphone
    if not mic_name or mic_name == "list":
        print("Showing available microphone devices: ")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f'Found microphone with name "{name}"')
        return Err("No microphone name provided, aborting.")
    else:
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if mic_name in name:
                source = sr.Microphone(sample_rate=16000, device_index=index)
                break
        else:
            return Err("Default microphone with name {mic_name} not found.")
    return Ok(source)


def initialize_source_recorder_with_queue(
    data_queue: TimedSampleQueue,
) -> tuple[sr.Microphone, sr.Recognizer]:
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = CONFIG.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False
    source = load_microphone_source().or_else(lambda err: exit(err)).unwrap()

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        data = audio.get_raw_data()
        data_queue.put((datetime.utcnow(), data))  # push bytes to thread-safe queue
        print(f"Received {len(data)} bytes of audio data.")

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    # here the recording is splitted to chunks of length <= phrase_max_second
    # or splitted by silence. It's not very few bytes.
    recorder.listen_in_background(
        source, record_callback, phrase_time_limit=CONFIG.phrase_max_second
    )
    return source, recorder


def load_whisper_model() -> whisper.Whisper:
    # Load / Download model
    model = CONFIG.model
    if CONFIG.source_lang == Language.EN and not model.endswith(".en"):
        model += ".en"
    print(f"Loading whisper model '{model}'")
    return whisper.load_model(model)


class ChunkedRecorder:
    data_queue: TimedSampleQueue
    source: sr.Microphone
    temp_wav: _TemporaryFileWrapper
    sample_rate_width: tuple[int, int]

    def __init__(self, data_queue: TimedSampleQueue):
        self.data_queue = data_queue
        self.source, _ = initialize_source_recorder_with_queue(data_queue)
        self.sample_rate_width = (self.source.SAMPLE_RATE, self.source.SAMPLE_WIDTH)

    def get_next_part(self) -> tuple[datetime, _TemporaryFileWrapper | None]:
        if self.data_queue.empty():
            return (datetime.utcnow(), None)
        # data_queue is not empty, handle the data.
        time, audio_buffer = self.data_queue.get()  # best way for Queue.
        # Convert raw data to wav file to return
        audio_data = sr.AudioData(audio_buffer, *self.sample_rate_width)
        temp_wav = NamedTemporaryFile()  # temp .wav file for whisper to read
        temp_wav.write(audio_data.get_wav_data())  # Write wav to the temp file
        return (time, temp_wav)


def real_time_transcribe() -> Transcriptions:
    # background thread to record audio data
    data_queue: TimedSampleQueue = Queue()  # thread-safe, store data from recording

    # output transcription
    transcription = Transcriptions(
        spontaneous_print=True, spontaneous_translator=get_translator()
    )

    whisper_model: whisper.Whisper = load_whisper_model()
    print("Model loaded. Recording...")  # Cue the user that we're ready to go.

    recorder = ChunkedRecorder(data_queue)

    while True:
        try:  # to not block the keyboard interrupt
            time, temp_wav = recorder.get_next_part()
            if temp_wav is None:
                sleep(0.1)
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
