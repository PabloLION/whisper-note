from datetime import datetime
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Static, Markdown, Label
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import ScrollableContainer
from whisper_note import Transcriber, CONFIG
from textual.reactive import reactive

# transcriber = Transcriber(CONFIG)

# from asyncio import sleep


class TranscriptionLine(Label):
    CSS = """
    TranscriptionLine {
        background: yellow;
        height: 2;
    }
    """

    def __init__(self, text: str, **kwargs):
        super().__init__(text, **kwargs)
        self.text = text


class TranscriptionScroller(ScrollableContainer):
    CSS = """
    TranscriptionLine {
        background: yellow;
        height: 2;
    }
    """

    def __init__(self, children: list[TranscriptionLine], **kwargs):
        super().__init__(*children, **kwargs)


class Transcription(Static):
    entries = reactive(["Transcription Content", ""])
    time_lapsed = reactive("")

    def compose(self):
        yield Label(id="time_lapsed")
        yield Label("Transcription:")
        yield TranscriptionScroller([], id="transcription-container")
        yield Button("Start Transcription")
        yield Button("Stop Transcription")

    def on_mount(self):
        self.update_timer = self.set_interval(1, self.update_all, pause=False)

    def update_all(self):
        self.update_entries()
        self.update_time_lapsed()

    def update_time_lapsed(self):
        self.time_lapsed = datetime.utcnow().strftime("%H:%M:%S.%f")

    def watch_time_lapsed(self, value: int):
        self.query_one("#time_lapsed", Label).update(
            f"Time Lapsed: {value} = {self.time_lapsed}"
        )

    def update_entries(self):
        self.entries.append("Hello" + datetime.utcnow().strftime("%H:%M:%S.%f")[:-3])

        container = self.query_one("#transcription-container", TranscriptionScroller)
        container._add_child(
            TranscriptionLine(
                self.entries[-1],
                id=f"transcription-content-{len(self.entries)}",
                classes="",
            )
        )
        container.scroll_end()


class Config(Screen):
    BINDINGS = [("escape,space,q,c", "pop_screen", "Close")]

    def compose(self):
        yield Header(show_clock=True)
        yield Markdown(str(CONFIG))  # #TODO: too ugly
        yield Footer()


class Export(Screen):  # #TODO: not implemented
    TITLE = "Export"
    BINDINGS = [("escape,space,q,c", "pop_screen", "Close")]

    def compose(self):
        yield Header(show_clock=True)
        yield Static("Fake Export Screen", classes="label")
        yield Footer()


class WhisperNoteApp(App):
    TITLE = "Whisper Note"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "push_screen('config')", "Config"),
        Binding("e", "push_screen('export')", "Export"),
        Binding("s", "screenshot()", "Screenshot"),
    ]
    SCREENS = {"config": Config, "export": Export}
    CSS = """
    Label {
        height: 2;
        background: red;
    }
    """

    def compose(self):
        self.dark_theme = True  # #TODO: use system theme
        yield Header(name="Whisper Note", show_clock=True)
        yield Transcription()
        yield Button("Load Model")
        yield Footer()

    def action_screenshot(self, filename: str | None = None, path: str = "./") -> None:
        """
        Save an SVG "screenshot".
        This action will save an SVG file containing the current contents of the screen.

        Args:
            filename: Filename of screenshot, or None to auto-generate.
            path: Path to directory.
        """
        self.bell()
        path = self.save_screenshot(filename, path)
        message = f"Screenshot saved to [bold green]'{(str(path))}'[/]"
        self.notify(message)


def run_textual_ui():
    WhisperNoteApp().run()


if __name__ == "__main__":
    run_textual_ui()
