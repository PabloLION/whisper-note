from datetime import datetime
from io import BufferedWriter
import os.path
from typing import Protocol, Sequence

from whisper_note.supportive_class import format_filename, format_local_time


WAV_HEADER_SIZE = 44  # suppose it's always 44 bytes


class SupportSeekAndRead(Protocol):
    def seek(self, offset: int, whence: int = 0) -> int:
        ...

    def read(self, n: int = -1) -> bytes:
        ...


def parse_path_config(path_config: str) -> str:
    """
    Return an absolute path to the new file, without extension.

    Input:
    - "" means nothing will be created.
    - "path/to/folder/" means "YYYY-MM-DD HH-MM-SS-ffffff" will be created there.
    - "path/to/file" means a file named "path/to/file" will be created at there.
    - Both "path/to/folder/" and "path/to/file" can be relative or absolute.
    - To encourage user to be aware if the path is a file or folder,
        "path/to/folder" and "path/to/file/" are not allowed.
    """
    path_config = path_config.strip()
    if path_config == "":
        return ""
    filename_no_ext = format_filename(format_local_time(datetime.now()))
    if path_config.endswith("/" or "\\"):
        assert os.path.isdir(path_config), f"{path_config} is not a folder"
        return os.path.join(path_config, filename_no_ext)
    else:
        assert not os.path.exists(path_config) or (
            os.path.isfile(path_config) and os.path.getsize(path_config) == 0
        ), f"{path_config} exists and is not empty, cannot write it"
        return os.path.abspath(path_config)


# #TEST_MISSING
def merge_wav_files(wav_files: Sequence[SupportSeekAndRead], output: BufferedWriter):
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
