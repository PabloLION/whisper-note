from collections import deque
import os
from datetime import datetime
from typing import Iterator
from whisper_note.cli import RichTable


from whisper_note.supportive_class import TranslatorProtocol, format_local_time

rich_table = RichTable()


class Transcriptions:
    """
    Will print upon updating the last phrase, unless told not to.
    """

    timestamp: list[datetime]
    time_str: list[str]
    text: list[str]
    translated_text: list[str]
    wav_sizes: list[int]
    # these five properties above are strongly coupled, should combine them.
    live_print: bool
    live_translator: TranslatorProtocol | None
    # maybe another full text translator
    clean_on_print: bool

    def __init__(
        self,
        live_print: bool,
        live_translator: TranslatorProtocol | None = None,
        clean_on_print: bool = True,
    ) -> None:
        self.timestamp = []
        self.text = []
        self.time_str = []
        self.wav_sizes = []
        self.translated_text = []
        self.live_print = live_print
        self.live_translator = live_translator
        self.clean_on_print = clean_on_print

    def add_phrase(self, timestamp: datetime, text: str, wav_size: int) -> None:
        if text.strip() == "":
            return
        self.timestamp.append(timestamp)
        self.time_str.append(format_local_time(timestamp))
        self.text.append(text)
        self.translated_text.append("")
        self.wav_sizes.append(wav_size)
        self.live_translate(len(self.text) - 1)

    def live_translate(self, index: int) -> str:
        # this should be exclusive, but we are only calling it once.
        assert 0 <= index < len(self.text), f"Transcriptions index {index} out of range"
        if not self.live_translator:
            return ""
        if self.translated_text[index] == "":
            translation = self.live_translator.translate(self.text[index])
            self.translated_text[index] = translation
        return self.translated_text[index]

    def format_for_rich(self) -> Iterator[tuple[str, str, int, bool, bool]]:
        yield from (
            (ts, txt + "\n" + tran, sz, True, bool(tran))
            for ts, txt, sz, tran, in zip(
                self.time_str, self.text, self.wav_sizes, self.translated_text
            )
        )

    # #TODO: add a no_truncate option
    def rich_print(self, pending_recordings: deque[tuple[datetime, int]]) -> None:
        rich_table.live_print(self.format_for_rich(), pending_recordings)

    # #TODO: add summary with ChatGPT
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
            yield self.time_str[i], self.text[i], self.translated_text[i]
            i += 1
