import os
from datetime import datetime
from typing import Iterator, Optional

from whisper_note.supportive_class import TranslatorProtocol


class Transcriptions:
    """
    Will print upon updating the last phrase, unless told not to.
    """

    timestamp: list[datetime]
    time_str: list[str]
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
        self.time_str = []
        self.translated_text = []
        self.spontaneous_print = spontaneous_print
        self.spontaneous_translator = spontaneous_translator
        self.clean_on_print = clean_on_print

    def add_phrase(self, timestamp: datetime, text: str) -> None:
        self.timestamp.append(timestamp)
        self.time_str.append(timestamp.strftime("%H:%M:%S:%f")[:-3])  # milliseconds
        self.text.append(text)
        self.translated_text.append("")

    def spontaneous_translate(self, index: int) -> str:
        assert 0 <= index < len(self.text), f"Transcriptions index {index} out of range"
        if not self.spontaneous_translator:
            return ""

        if self.translated_text[index] == "":
            translation = self.spontaneous_translator.translate(self.text[index])
            self.translated_text[index] = translation
        return self.translated_text[index]

    def print_phrase(self, index: int, with_time: bool = False) -> None:
        indent_len = 15 if with_time else 0  # 15==len("HH:MM:SS:fff | ")
        if with_time:
            print(self.time_str[index], end=" | ")
        print(self.text[index])
        if self.spontaneous_translator:
            print(" " * indent_len + self.spontaneous_translate(index))

    def print_all(self, *, with_time: bool = True, clean: bool = False) -> None:
        # Reprint the updated transcription to a cleared terminal.
        if clean:
            os.system(self.__CLEAR_COMMAND)
        for index in range(len(self.text)):
            self.print_phrase(index, with_time)
        print("", end="", flush=True)

    def clear(self) -> None:  # never used
        self.timestamp.clear()
        self.time_str.clear()
        self.text.clear()
        self.translated_text.clear()

    def __str__(self) -> str:
        return "\n".join(self.text)

    def __repr__(self) -> str:
        return f"Transcripts({self.timestamp}, {self.text})"

    def __len__(self) -> int:
        return len(self.text)

    def __iter__(self) -> Iterator[tuple[str, str, str] | None]:
        i = 0
        while True:
            if i >= len(self):
                yield None
            yield self.time_str[i], self.text[i], self.spontaneous_translate(i)
            i += 1
