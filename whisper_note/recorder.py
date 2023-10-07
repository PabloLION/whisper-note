from datetime import datetime
from sys import platform
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

import speech_recognition as sr
from result import Err, Ok, Result
from supportive_class import FrozenConfig, TimedSampleQueue


class ChunkedRecorder:
    """
    Record audio in chunks in a background thread and return the
    chunks as wav files.
    """

    data_queue: TimedSampleQueue
    source: sr.Microphone
    temp_wav: _TemporaryFileWrapper
    sample_rate_width: tuple[int, int]
    config: FrozenConfig

    def __init__(self, data_queue: TimedSampleQueue, config: FrozenConfig):
        self.config = config
        self.data_queue = data_queue
        self.source, _ = self.initialize_source_recorder_with_queue()
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

    def load_microphone_source(self) -> Result[sr.Microphone, str]:
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

    def initialize_source_recorder_with_queue(
        self,
    ) -> tuple[sr.Microphone, sr.Recognizer]:
        # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
        recorder = sr.Recognizer()
        recorder.energy_threshold = self.config.energy_threshold
        # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
        recorder.dynamic_energy_threshold = False
        source = self.load_microphone_source().or_else(lambda err: exit(err)).unwrap()

        with source:
            recorder.adjust_for_ambient_noise(source)

        def record_callback(_, audio: sr.AudioData) -> None:
            """
            Threaded callback function to receive audio data when recordings finish.
            audio: An AudioData containing the recorded bytes.
            """
            data = audio.get_raw_data()
            self.data_queue.put(
                (datetime.utcnow(), data)
            )  # push bytes to thread-safe queue
            print(f"Received {len(data)} bytes of audio data.")

        # Create a background thread that will pass us raw audio bytes.
        # We could do this manually but SpeechRecognizer provides a nice helper.
        # here the recording is splitted to chunks of length <= phrase_max_second
        # or splitted by silence. It's not very few bytes.
        recorder.listen_in_background(
            source, record_callback, phrase_time_limit=self.config.phrase_max_second
        )
        return source, recorder
