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

SampleQueue = Queue[bytes]


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
    data_queue: SampleQueue,
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
        data_queue.put(data)  # push the raw bytes to the thread safe queue.
        print(f"Received {len(data)} bytes of audio data.")

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
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
    data_queue: SampleQueue
    source: sr.Microphone
    phrase_max_second = timedelta(seconds=CONFIG.phrase_max_second)
    phrase_timestamp = datetime.min  # Timestamp of last phrase. Force new phrase
    audio_buffer: bytes  # Current raw audio bytes.
    temp_wav: _TemporaryFileWrapper

    def __init__(self, data_queue: SampleQueue):
        self.data_queue = data_queue
        self.source, _ = initialize_source_recorder_with_queue(data_queue)
        self.audio_buffer = bytes()

    def get_next_part(self) -> _TemporaryFileWrapper | None:
        if self.data_queue.empty():
            sleep(0.1)
            return None

        # data_queue is not empty, handle the data.
        now = datetime.utcnow()

        # If enough time has passed between recordings, consider the phrase complete.
        # Clear the current audio buffer to start over with the new data.
        is_new_phrase = now - self.phrase_timestamp > self.phrase_max_second
        if is_new_phrase:
            self.audio_buffer = bytes()
            # keep audio_timestamp the same
        else:
            self.phrase_timestamp = now
            # keep audio_sample the same

        # Concatenate our current audio data with the latest audio data.
        while not self.data_queue.empty():  # there's no better way for Queue.
            self.audio_buffer += self.data_queue.get()

        # Convert the raw data to wav AudioData.
        audio_data = sr.AudioData(
            self.audio_buffer, self.source.SAMPLE_RATE, self.source.SAMPLE_WIDTH
        )
        wav_bytes = io.BytesIO(audio_data.get_wav_data())

        temp_wav = NamedTemporaryFile()  # new temp file to aggregate audio data
        temp_wav.write(wav_bytes.read())  # Write wav bytes to the temp file
        return temp_wav


def real_time_transcribe() -> Transcriptions:
    # background thread to record audio data
    data_queue: SampleQueue = Queue()  # thread-safe, store data from recording

    # output transcription
    transcription = Transcriptions(
        spontaneous_print=True, spontaneous_translator=get_translator()
    )

    whisper_model: whisper.Whisper = load_whisper_model()
    print("Model loaded. Recording...")  # Cue the user that we're ready to go.

    recorder = ChunkedRecorder(data_queue)

    while True:
        try:  # to not block the keyboard interrupt
            temp_wav = recorder.get_next_part()
            if temp_wav is None:
                sleep(0.1)
                continue

            # Get transcription from the model.
            transcribed = whisper_model.transcribe(
                temp_wav.name, fp16=torch.cuda.is_available()
            )
            text = cast(str, transcribed["text"]).strip()

            # #FIX: wrong comment
            # Add new item to transcription, or append to the existing last phrase.
            transcription.new_phrase()
            transcription.update_last(text)

        except KeyboardInterrupt:
            break

    transcription.print_all()
    print("Stopping recording...")

    return transcription
