import os
from datetime import datetime
from typing import Iterator, Optional
from whisper_note.cli import RichTable


from whisper_note.supportive_class import TranslatorProtocol, CLEAR_COMMAND

rich_table = RichTable()


class Transcriptions:
    """
    Will print upon updating the last phrase, unless told not to.
    """

    timestamp: list[datetime]
    time_str: list[str]
    text: list[str]
    translated_text: list[str]
    real_time_print: bool
    real_time_translator: Optional[TranslatorProtocol]
    # maybe another full text translator
    clean_on_print: bool

    def __init__(
        self,
        real_time_print: bool,
        real_time_translator: Optional[TranslatorProtocol],
        clean_on_print: bool = True,
    ) -> None:
        self.timestamp = []
        self.text = []
        self.time_str = []
        self.translated_text = []
        self.real_time_print = real_time_print
        self.real_time_translator = real_time_translator
        self.clean_on_print = clean_on_print

    def add_phrase(self, timestamp: datetime, text: str) -> None:
        if text.strip() == "":
            return
        self.timestamp.append(timestamp)
        # FIX: wrong time format UTC+0
        self.time_str.append(timestamp.strftime("%H:%M:%S:%f")[:-3])  # milliseconds
        self.text.append(text)
        self.translated_text.append("")
        self.real_time_translate(len(self.text) - 1)

    def real_time_translate(self, index: int) -> str:
        # this should be exclusive, but we are only calling it once.
        assert 0 <= index < len(self.text), f"Transcriptions index {index} out of range"
        if not self.real_time_translator:
            return ""
        if self.translated_text[index] == "":
            translation = self.real_time_translator.translate(self.text[index])
            self.translated_text[index] = translation
        return self.translated_text[index]

    def format_for_rich(self) -> Iterator[tuple[str, str, bool, bool]]:
        yield from (
            (ts, txt + "\n" + tran, True, bool(tran))
            for ts, txt, tran in zip(self.time_str, self.text, self.translated_text)
        )

    # #TODO: show pending record time
    def rich_print(self, n_pending_transcribe: int) -> None:
        rich_table.print_to_save(self.format_for_rich(), n_pending_transcribe)

    def print_phrase(self, index: int, with_time: bool = False) -> None:
        indent_len = 15 if with_time else 0  # 15==len("HH:MM:SS:fff | ")
        if with_time:
            print(self.time_str[index], end=" | ")
        print(self.text[index])
        if self.real_time_translator:
            print(" " * indent_len + self.translated_text[index])

    def print_all(self, *, with_time: bool = True, clean: bool = False) -> None:
        # Reprint the updated transcription to a cleared terminal.
        if clean:
            os.system(CLEAR_COMMAND)
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
        # #TODO: test if two iters will conflict
        i = 0
        while True:
            if i >= len(self):
                yield None
            yield self.time_str[i], self.text[i], self.translated_text[i]
            i += 1
