from textual.app import App
from textual.widgets import Footer, Header, Button


class WhisperNoteApp(App):
    def compose(self):
        yield Header(name="Whisper Note", show_clock=True)
        yield Button("Load Model")
        yield Button("Start Transcription")
        yield Button("Stop Transcription")
        yield Button("Export...")
        yield Button("Settings...")
        yield Button("Quit")
        yield Footer()


def run_textual_ui():
    WhisperNoteApp().run()
