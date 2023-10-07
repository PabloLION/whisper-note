import argparse
from sys import platform
from typing import Final
from rich.console import Console
from rich.table import Table


def build_default_args() -> argparse.Namespace:
    # #TODO: load args from cli and parse it to typed frozen config file
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
    table: Table

    @property
    def screen_width(self) -> int:
        return self.console.width

    def __init__(self) -> None:
        self.console = Console()

        table = Table(
            show_header=True,
            header_style="bold magenta",
            title="Transcripts",
            expand=True,
            show_lines=True,
            show_edge=False,
        )
        time_width = 11
        checker_width = 4
        text_width = self.console.width - time_width - checker_width * 2 - 3 * 5
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
        table.add_column("EN", justify="center", width=checker_width)
        table.add_column("CN", justify="center", width=checker_width)

        table.add_row(
            "00:00:00:000",
            "Hello, world!\n你好，世界！",
            "✓",
            "_",
        )
        table.add_row(
            "00:00:00:000",
            "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco\n你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！你好，世界！",
            "✓",
            "_",
        )

    def print(self) -> None:
        self.console.print(self.table)
