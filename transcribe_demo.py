#! python3.7

import argparse
import io
import os
from datetime import datetime, timedelta
from queue import Queue
from sys import platform
from tempfile import NamedTemporaryFile
from time import sleep
from typing import cast

import speech_recognition as sr
import torch
import whisper
from result import Err, Ok, Result


def build_args() -> argparse.Namespace:
    # this build a default args, but we should #TODO:
    # 1. load args from a config file
    # 2. maybe use a typed dict instead of argparse.Namespace
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="medium",
        help="Model to use",
        choices=["tiny", "base", "small", "medium", "large"],
    )
    parser.add_argument(
        "--non_english", action="store_true", help="Don't use the english model."
    )
    parser.add_argument(
        "--energy_threshold",
        default=1000,
        help="Energy level for mic to detect.",
        type=int,
    )
    parser.add_argument(
        "--record_timeout",
        default=2,
        help="How real time the recording is in seconds.",
        type=float,
    )
    parser.add_argument(
        "--phrase_timeout",
        default=3,
        help="How much empty space between recordings before we "
        "consider it a new line in the transcription.",
        type=float,
    )
    if "linux" in platform:
        parser.add_argument(
            "--default_microphone",
            default="pulse",
            help="Default microphone name for SpeechRecognition. "
            "Run this with 'list' to view available Microphones.",
            type=str,
        )
    args = parser.parse_args()
    return args


def load_microphone_source(args) -> Result[sr.Microphone, str]:
    # Important for linux users.
    # Prevents permanent application hang and crash by using the wrong Microphone
    if "linux" in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == "list":
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f'Microphone with name "{name}" found')
            return Err("No microphone name provided, aborting.")
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
            else:
                print(f"No microphone with name {mic_name} found, aborting.")
                return Err("No microphone with name {mic_name} found, aborting.")
    else:
        source = sr.Microphone(sample_rate=16000)
    return Ok(source)


# def load_whisper_model(args) -> Result[whisper.Whisper, str]:
def initialize_source_recorder_with_queue(
    args: argparse.Namespace, data_queue: Queue
) -> tuple[sr.Microphone, sr.Recognizer]:
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    source = load_microphone_source(args).or_else(lambda err: exit(err)).unwrap()

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(
        source, record_callback, phrase_time_limit=args.record_timeout
    )
    return source, recorder


def load_model(args) -> whisper.Whisper:
    # Load / Download model
    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"
    print(f"Loading whisper model '{model}'")
    return whisper.load_model(model)


def main():
    args = build_args()
    args.model = "large"  # #TODO: add a config file

    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    audio_model = load_model(args)
    source, _ = initialize_source_recorder_with_queue(args, data_queue)
    print("Model loaded. Recording...")  # Cue the user that we're ready to go.

    phrase_timeout = timedelta(seconds=args.phrase_timeout)
    phrase_timestamp = datetime.utcnow()  # The last time of retrieved data.
    # #TODO merge this into the queue to show time stamp
    current_audio_bytes = bytes()  # Current raw audio bytes.
    transcription = [""]

    while True:
        try:  # to not block the keyboard interrupt
            if data_queue.empty():
                sleep(0.1)
                continue
        except KeyboardInterrupt:
            break

        # data_queue is not empty, handle the data.
        temp_wav = NamedTemporaryFile()
        now = datetime.utcnow()
        # If enough time has passed between recordings, consider the phrase complete.
        # Clear the current working audio buffer to start over with the new data.
        if now - phrase_timestamp > phrase_timeout:
            phrase_complete = True  # show call this "is_new_phrase"
            current_audio_bytes = bytes()
            # keep phrase_timestamp the same
        else:
            phrase_complete = False
            phrase_timestamp = now
            # keep current_audio_bytes the same

        # Concatenate our current audio data with the latest audio data.
        while not data_queue.empty():
            data = data_queue.get()
            current_audio_bytes += data

        # Use AudioData to convert the raw data to wav data.
        audio_data = sr.AudioData(
            current_audio_bytes, source.SAMPLE_RATE, source.SAMPLE_WIDTH
        )
        wav_bytes = io.BytesIO(audio_data.get_wav_data())
        temp_wav.write(wav_bytes.read())  # Write wav bytes to the temp file

        # Read the transcription.
        result = audio_model.transcribe(temp_wav.name, fp16=torch.cuda.is_available())
        text = cast(str, result["text"]).strip()

        # pause detected between recordings, add new item to transcription.
        if phrase_complete:
            transcription.append(text)
        else:  # Otherwise edit the existing one.
            transcription[-1] = text

        # Reprint the updated transcription to a cleared terminal.
        os.system("cls" if os.name == "nt" else "clear")  # #TODO: extract
        for line in transcription:
            print(line)
        print("", end="", flush=True)  # Flush stdout.

    print("\n\nTranscription:")
    for line in transcription:
        print(line)


if __name__ == "__main__":
    main()
