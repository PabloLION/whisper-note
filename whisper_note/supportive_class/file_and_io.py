from io import BufferedReader, BufferedWriter
import os

WAV_HEADER_SIZE = 44  # suppose it's always 44 bytes


def merge_wav_files(wav_files: list[BufferedReader], output: BufferedWriter):
    assert len(wav_files) > 0, "No wav files to merge"
    assert output.writable(), f"{output.name} is not writable"
    assert os.path.exists(output.name), f"{output.name} not found"
    assert os.path.getsize(output.name) == 0, f"{output.name} is not empty"

    # the 44 bytes header, line numbers end on same digit -> 11 lines
    output.write(b"RIFF")
    output.write(b"\x00\x00\x00\x00")
    output.write(b"WAVE")
    output.write(b"fmt ")
    output.write(b"\x10\x00\x00\x00")
    output.write(b"\x01\x00\x01\x00")
    output.write(b"\x80\x3e\x00\x00")
    output.write(b"\x00\x7d\x00\x00")
    output.write(b"\x02\x00\x10\x00")
    output.write(b"data")
    output.write(b"\x00\x00\x00\x00")

    for wav in wav_files:
        wav.seek(0)
        wav.seek(WAV_HEADER_SIZE)
        output.write(wav.read())
        wav.close()
