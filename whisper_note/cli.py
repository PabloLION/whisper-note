import argparse
import sys
from datetime import datetime
from io import StringIO
from typing import Iterator, Sequence

from rich import print
from rich.console import Console
from rich.live import Live
from rich.table import Table
from whisper_note.supportive_class import LOG, format_bytes_str, format_local_time


def scroll_down(lines):
    if "darwin" in sys.platform:
        # sys.stdout.write(f"\033[{lines}T")  # Scroll down by 'lines' lines
        sys.stdout.flush()
    elif "win" in sys.platform:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore , from ChatGPT
        handle = kernel32.GetStdHandle(-11)  # Standard Output Handle
        kernel32.ScrollConsoleScreenBufferW(handle, 0, None, (lines, lines), None)
    elif "linux" in sys.platform:
        LOG.warning(f"cannot scroll down {lines} lines on {sys.platform}")
    else:
        raise NotImplementedError(f"Unknown sys.platform: {sys.platform}")


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

    def _build_live_table(  # #TODO: ren: _construct_new_rich_table
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        n_pending_transcribe: Sequence[tuple[datetime, int]],
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
        for time, size in n_pending_transcribe:
            table.add_row(format_local_time(time), "", format_bytes_str(size), "_", "_")
        return table

    def live_print(
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        n_pending_transcribe: Sequence[tuple[datetime, int]],
    ):
        # #TODO: show current time
        table = self._build_live_table(table_content, n_pending_transcribe)
        self.live_console.update(table, refresh=True)

    def save_history_html(
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        html_path: str,
    ):
        # #TODO:LTR the html has bad styling... Even worse than SVG
        table = self._build_live_table(table_content, [])
        output_buffer = StringIO()
        with Console(file=output_buffer, record=True) as console:
            console.print(table)
            console.save_html(html_path)

    def save_table(  # #TODO: ren save_history_str
        self,
        table_content: Iterator[tuple[str, str, int, bool, bool]],
        n_pending_transcribe: Sequence[tuple[datetime, int]],  # #TODO: ren: rm n_
        html_path: str | None = None,
    ) -> str:
        table = self._build_live_table(table_content, n_pending_transcribe)
        output_buffer = StringIO()
        str_console = Console(file=output_buffer, record=True)
        str_console.print(table)
        if html_path:
            str_console.save_html(html_path)
        console_str = output_buffer.getvalue()
        return console_str  # console_str  # for testing
