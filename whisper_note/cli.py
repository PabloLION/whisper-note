import argparse
from pathlib import Path
import sys
from datetime import datetime
from io import StringIO
from typing import Iterator, Sequence

from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.align import Align
from whisper_note.supportive_class import format_bytes_str, format_local_time


def build_default_args() -> argparse.Namespace:
    # #TODO:LTR load args from cli and parse it to FrozenConfig
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
    if "linux" in sys.platform:
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
    live_console: Live

    def __init__(self) -> None:
        self.console = Console()
        self.live_console = Live(
            console=self.console, vertical_overflow="visible", auto_refresh=False
        ).__enter__()

    def _new_table_with_col(self) -> Table:
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
        # #TODO: use realistic lang headers from config
        table.add_column("EN", justify="center", width=checker_width)
        table.add_column("CN", justify="center", width=checker_width)
        return table

    def _construct_new_table(
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        pending_time_size: Sequence[tuple[datetime, int]],
    ) -> Table:
        # Instead of re-building the whole table, we may use `table.rows.__delitem__()`
        # BUT, the width of the table will not be updated, so maybe it's not a good idea.
        table = self._new_table_with_col()
        for time, text, sz, transcribed, translated in table_content:
            c = lambda x: "✓" if x else "_"  # to check char
            table.add_row(
                time,
                text,
                format_bytes_str(sz),
                c(transcribed),  # do we actually need to pass this?
                c(translated),
                end_section=True,
            )
        for time, size in pending_time_size:
            table.add_row(format_local_time(time), "", format_bytes_str(size), "_", "_")
        return table

    def live_print(
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        pending_time_size: Sequence[tuple[datetime, int]],
    ):
        table = self._construct_new_table(table_content, pending_time_size)
        self.live_console.update(
            Group(table, self._centered_time()),
            refresh=True,
        )

    def save_history_html(
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        html_path: Path,
    ):
        # #TODO:LTR the html has bad styling... Even worse than SVG
        table = self._construct_new_table(table_content, [])
        output_buffer = StringIO()
        with Console(file=output_buffer, record=True) as console:
            console.print(table)
            console.save_html(str(html_path))

    def gen_history_str(
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        pending_time_size: Sequence[tuple[datetime, int]],
    ) -> str:
        table = self._construct_new_table(table_content, pending_time_size)
        output_buffer = StringIO()
        str_console = Console(file=output_buffer, record=True)
        str_console.print(table)
        return output_buffer.getvalue()  # for testing

    @staticmethod
    def _centered_time() -> Align:
        return Align(format_local_time(datetime.now()), "center")
