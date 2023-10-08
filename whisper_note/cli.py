import argparse
from collections import deque
from datetime import datetime
import os
from sys import platform
from typing import Iterator
from rich.console import Console
from rich.table import Table

from whisper_note.supportive_class import (
    CLEAR_COMMAND,
    convert_bytes,
    format_local_time,
)


def build_default_args() -> argparse.Namespace:
    # #TODO: load args from cli and parse it to FrozenConfig
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
        "--phrase_max_second",
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


class RichTable:
    console: Console

    @property
    def screen_width(self) -> int:
        return self.console.width

    def __init__(self) -> None:
        self.console = Console(record=True)

    def new_table(self) -> Table:
        time_width = 14
        checker_width = 4
        size_width = 6
        text_width = self.console.width - time_width - checker_width * 2 - 3 * 6

        table = Table(
            show_header=True,
            header_style="bold magenta",
            title="Transcripts",
            expand=True,
            show_edge=False,
        )
        table.add_column(
            "Time",
            style="dim",
            justify="center",
            vertical="middle",
            width=time_width,
        )
        table.add_column(
            "Text & Translation", justify="left", width=text_width, overflow="fold"
        )
        table.add_column("Size", justify="center", width=size_width)
        # #TODO:use realistic lang headers from config
        table.add_column("EN", justify="center", width=checker_width)
        table.add_column("CN", justify="center", width=checker_width)
        return table

    def print_to_save(
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        n_pending_transcribe: deque[tuple[datetime, int]],
        html_path: str | None = None,
    ) -> str:
        self.console.clear(home=False)
        os.system(CLEAR_COMMAND)
        table = self.new_table()
        for time, text, sz, transcribed, translated in table_content:
            c = lambda x: "✓" if x else "_"  # to check char
            table.add_row(
                time,
                text,
                convert_bytes(sz),
                c(transcribed),  # do we actually need to pass this?
                c(translated),
                end_section=True,
            )
        for time, size in n_pending_transcribe:
            table.add_row(format_local_time(time), "", convert_bytes(size), "_", "_")
        self.console.print(table)
        if html_path:
            self.console.save_html(html_path)
        self.console.print(" ")
        print("", end="", flush=True)  # scroll to bottom
        return self.console.export_text()  # for testing
