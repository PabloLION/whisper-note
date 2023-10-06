import os
from datetime import datetime
from textwrap import indent
from typing import Optional

from whisper_note.translate import TranslatorProtocol


class Transcriptions:
    """
    Will print upon updating the last phrase, unless told not to.
    """

    timestamp: list[datetime]
    text: list[str]
    spontaneous_print: bool
    spontaneous_translator: Optional[TranslatorProtocol]

    __CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"

    def __init__(
        self,
        spontaneous_print: bool,
        spontaneous_translator: Optional[TranslatorProtocol],
    ) -> None:
        self.timestamp = []
        self.text = []
        self.spontaneous_print = spontaneous_print
        self.spontaneous_translator = spontaneous_translator

    def new_phrase(self) -> None:
        self.timestamp.append(datetime.utcnow())
        self.text.append("")

    def update_last(self, text: str) -> None:
        self.text[-1] = text
        if self.spontaneous_print:
            self.print(clear=True)

    def clear(self) -> None:  # never used
        self.timestamp.clear()
        self.text.clear()

    def print(self, *, show_time: bool = True, clear: bool = False) -> None:
        # Reprint the updated transcription to a cleared terminal.
        if clear:
            os.system(self.__CLEAR_COMMAND)
        for timestamp, text in zip(self.timestamp, self.text):
            if not show_time:
                print(text)
                continue
            ts_text = timestamp.strftime("%H:%M:%S:%f")[:-3]  # milliseconds
            print(f"{ts_text} | {text}")  # #TODO: consider line wrap for text
        print("", end="", flush=True)

    def __str__(self) -> str:
        return "\n".join(self.text)

    def __repr__(self) -> str:
        return f"Transcripts({self.timestamp}, {self.text})"
