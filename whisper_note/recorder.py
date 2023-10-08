import os
from collections import deque
from datetime import datetime
from io import BufferedWriter
from sys import platform
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

import speech_recognition as sr
from result import Err, Ok, Result

from whisper_note.supportive_class.file_and_io import merge_wav_files

from .supportive_class import FrozenConfig, WavTimeSizeQueue


class ChunkedRecorder:
    """
    Record audio in chunks in a background thread and return the
    chunks as wav files.
    """

    data_queue: WavTimeSizeQueue  # coupled to pending_time_size, should combine
    pending_time_size: deque[tuple[datetime, int]]
    source: sr.Microphone
    temp_wav: _TemporaryFileWrapper
    sample_rate_width: tuple[int, int]
    config: FrozenConfig
    all_wav: list[_TemporaryFileWrapper]

    def __init__(self, data_queue: WavTimeSizeQueue, config: FrozenConfig):
        self.config = config
        self.data_queue = data_queue
        self.pending_time_size = deque()
        self.source, _ = self._initialize_recorder_source()
        self.sample_rate_width = (self.source.SAMPLE_RATE, self.source.SAMPLE_WIDTH)
        self.all_wav = []

    def get_next_part(self) -> tuple[_TemporaryFileWrapper | None, datetime, int]:
        if self.data_queue.empty():
            return (None, datetime.now(), 0)  # no data yet, return None.
        # data_queue is not empty, handle the data.
        temp_wav, time, size = self.data_queue.get()  # best way for Queue.
        self.pending_time_size.popleft()
        return (temp_wav, time, size)

    def gen_full_wav(self) -> None:
        """merge all wav files in self.all_wav to a single wav file"""
        if not self.config.store_merged_wav:  # double checking is good
            return
        with open(self.config.store_merged_wav, "ab") as merged_wav:
            merge_wav_files(self.all_wav, merged_wav)

    def _load_microphone_source(self) -> Result[sr.Microphone, str]:
        if "linux" not in platform:
            source = sr.Microphone(sample_rate=16000)
            return Ok(source)

        # only Linux users need this to prevent permanent application hang / crash
        mic_name = self.config.linux_microphone
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

    def _record_callback(self, _, audio: sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Convert raw data to wav file before pushing it to the queue.
        temp_wav = NamedTemporaryFile(delete=self.config.store_merged_wav == "")
        temp_wav.write(audio.get_wav_data())  # temp .wav file for whisper to read
        time, size = datetime.now(), os.path.getsize(temp_wav.name)
        if self.config.store_merged_wav:
            self.all_wav.append(temp_wav)
        self.data_queue.put((temp_wav, time, size))
        self.pending_time_size.append((time, size))
        # push bytes to thread-safe queue
        print(f"Received {size} bytes of wav data.")

    def _initialize_recorder_source(self) -> tuple[sr.Microphone, sr.Recognizer]:
        # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
        recorder = sr.Recognizer()
        recorder.energy_threshold = self.config.energy_threshold
        # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
        recorder.dynamic_energy_threshold = False
        source = self._load_microphone_source().or_else(lambda err: exit(err)).unwrap()

        with source:
            recorder.adjust_for_ambient_noise(source)

        # Create a background thread that will pass us raw audio bytes.
        # We could do this manually but SpeechRecognizer provides a nice helper.
        # here the recording is splitted to chunks of length <= phrase_max_second
        # or splitted by silence. It's not very few bytes.
        recorder.listen_in_background(
            source,
            self._record_callback,
            phrase_time_limit=self.config.phrase_max_second,
        )
        return source, recorder
