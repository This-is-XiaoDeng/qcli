from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static
from textual.containers import Container
import sys


class Chat(Static):
    text = {"start": "[green]IT Craft QCli Version 1.2\nBy XiaoDeng3386[/]"}
    selected_screen = "start"

    # def (self):
    #    text = "QCli Version 1.2\nBy XiaoDeng3386"
    #    self.update(self.text)

    def clean(self):
        self.text[self.selected_screen] = "[green]IT Craft QCli Version 1.2[/]"
        self.update(self.text[self.selected_screen])

    def edit(self, value):
        self.text[self.selected_screen] += f"\n{value}"
        self.update(self.text[self.selected_screen])
        self.scroll_end()

    def init(self):
        self.edit("")

    def set_screen(self, screen):
        if screen in self.text.keys():
            self.selected_screen = screen
            self.update(self.text[self.selected_screen])
        else:
            self.text[self.selected_screen] = ""
            self.selected_screen = screen
            self.clean()


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
    BINDINGS = [  # ("d", "toggle_dark", "Toggle dark mode"),
        ("escape", "reset_focus", "Reset Input"),
        ("ctrl+q", "quit_app", "Quit")]
    CSS_PATH = "stylesheet.css"
    TITLE = "IT CRAFT QCLI Version 1.2"

    async def action_quit_app(self) -> None:
        sys.exit()

    def compose(self) -> ComposeResult:
        self.chat = Chat()
        self.group_list = Static()
        self.statusbar_grouplist = Static()
        self.chat.init()
        self.gocqlog = Static(classes="box2")
        self.user_status = Static("User: <none> (<none>)")
        self.statusbar = Container(
            self.user_status,
            self.statusbar_grouplist,
            self.gocqlog,
            classes="box"
        )
        self.input = Input(classes="box", id="two")
        
        yield Header(show_clock=True)
        yield Footer()
        yield Container(self.chat, self.group_list, classes="box")
        yield self.statusbar
        yield self.input

    def set_group(self, group):
        self.group_list.set_styles("display: none;")
        self.chat.set_screen(f"g{group}")

    def update_groups_list(self, groups) -> None:
        self.group_list.update(groups)
        self.statusbar_grouplist.update(groups)

    async def on_input_submitted(self, event) -> None:
        # self.chat.edit(event.value)
        await self.send_func(event.value)
        self.input.value = ""

    def action_reset_input(self) -> None:
        self.input.value = ""
        self.input.reset_focus()

    def add_message(self, text) -> None:
        self.chat.edit(text)

    def set_send_func(self, func) -> None:
        self.send_func = func
