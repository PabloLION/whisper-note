import os
from datetime import datetime
from textwrap import indent
from typing import Optional

from sympy import O

from whisper_note.supportive_class import TranslatorProtocol


class Transcriptions:
    """
    Will print upon updating the last phrase, unless told not to.
    """

    timestamp: list[datetime]
    text: list[str]
    translated_text: list[str]
    spontaneous_print: bool
    spontaneous_translator: Optional[TranslatorProtocol]
    # maybe another full text translator
    clean_on_print: bool

    __CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"

    def __init__(
        self,
        spontaneous_print: bool,
        spontaneous_translator: Optional[TranslatorProtocol],
        clean_on_print: bool = True,
    ) -> None:
        self.timestamp = []
        self.text = []
        self.translated_text = []
        self.spontaneous_print = spontaneous_print
        self.spontaneous_translator = spontaneous_translator
        self.clean_on_print = clean_on_print

    def new_phrase(self, timestamp: datetime, text: str) -> None:
        self.timestamp.append(timestamp)
        self.text.append(text)
        self.translated_text.append("")

    def clear(self) -> None:  # never used
        self.timestamp.clear()
        self.text.clear()

    def print_phrase(self, index: int, with_time: bool) -> None:
        indent_len = 0
        if with_time is not None:
            ts_text = self.timestamp[index].strftime("%H:%M:%S:%f")[:-3]  # milliseconds
            indent_len = len(ts_text) + 3
            print(ts_text, end=" | ")
        print(self.text[index])
        if self.spontaneous_translator:
            if self.translated_text[index] == "":
                translation = self.spontaneous_translator.translate(self.text[index])
                self.translated_text[index] = translation
            print(" " * indent_len + self.translated_text[index])

    def print_all(self, *, with_time: bool = True, clean: bool = False) -> None:
        # Reprint the updated transcription to a cleared terminal.
        if clean:
            os.system(self.__CLEAR_COMMAND)
        for index in range(len(self.text)):
            self.print_phrase(index, with_time)
        print("", end="", flush=True)

    def __str__(self) -> str:
        return "\n".join(self.text)

    def __repr__(self) -> str:
        return f"Transcripts({self.timestamp}, {self.text})"
