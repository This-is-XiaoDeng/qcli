from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static
from textual.containers import Container


class Chat(Static):
    text = "[green]IT Craft QCli Version 1.2\nBy XiaoDeng3386[/]"

    #def (self):
    #    text = "QCli Version 1.2\nBy XiaoDeng3386"
    #    self.update(self.text)

    def edit(self, value, a=True):
        self.text += f"\n{value}"
        self.update(self.text)
        self.scroll_end()


"""
class Input(Static):
    text = ""
    def insert(self, text):
        #if text == "backspace":
        #    self.text = self.text[:-1]
        #elif text == "space":
        #    self.text += " "
        #else:
        self.text += text
        self.update(self.text + "_")
"""


class QCli(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("escape", "reset_focus", "Exit Input")]
    CSS_PATH = "vertical_layout.css"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        self.chat = Chat()
        yield Container(self.chat, classes="box")
        yield Static("Seesions", classes="box")
        # self.input = Input()
        # yield Container(self.input, classes="box", id="two")#Static("Input", classes="box", id="two")
        self.input = Input(classes="box", id="two")
        yield self.input

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    async def on_input_submitted(self, event) -> None:
        # self.chat.edit(event.value)
        await self.send_func(event.value)
        self.input.value = ""

    def action_reset_focus(self) -> None:
        self.input.reset_focus()

    def add_message(self, text) -> None:
        self.chat.edit(text)

    def set_send_func(self, func) -> None:
        self.send_func = func

    # def on_key(self, event: events.Key):
    #    self.input.insert(event.char)


#app = QCli()
# app.run()
