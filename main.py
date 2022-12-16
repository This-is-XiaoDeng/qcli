import rich.markdown
from aiocqhttp import CQHttp
import parser
import asyncio
from aiocqhttp import Event
import rich.console
import app
import rich.table
import json
import threading
import subprocess
import traceback


class qCli():
    config = json.load(open("./config.json"))
    bot = CQHttp(
        api_root=config["go-cqhttp"]["api_root"],
        access_token=config["go-cqhttp"]["access_token"],
        secret=config["go-cqhttp"]["secret"]
    )
    selected_session = None
    group_mode = True
    ui = app.QCli()
    console = rich.console.Console()
    aliases = json.load(open("./aliases.json"))
    new_messages: dict = {}
    self_nick = None
    self_id = None
    cqhttp_popen = None

    def display_cqhttp_logger(self):
        while True:
            buffer = self.cqhttp_popen.stdout.readline().decode()
            if buffer != "" and self.cqhttp_popen.poll() is not None:
                break
            buffer = buffer[buffer.find(" [")+1:].replace("\n", "")
            if self.self_nick is not None:
                self.ui.gocqlog.update(buffer)
            else:
                self.console.print(buffer)

    def __init__(self):
        with open("config.yml") as f:
            cqhttp_config = f.read()
        cqhttp_config = cqhttp_config\
            .replace("{{uin}}", self.config["user"]["uin"])\
            .replace("{{password}}", self.config["user"]["password"])\
            .replace("{{ws-port}}", self.config["port"])\
            .replace("{{http-addr}}", self.config["go-cqhttp"]["api_root"]
                     .replace("http://", ""))\
            .replace(
                "{{access-token}}", self.config["go-cqhttp"]["access_token"])
        with open("./go-cqhttp/config.yml", "w") as f:
            self.console.rule("config.yml")
            self.console.print(rich.markdown.Markdown(
                f"```yaml\n{cqhttp_config}\n```"))
            self.console.rule("(END)")
            f.write(cqhttp_config)
        # self.gocq = os.popen("cd ./go-cqhttp/;./go-cqhttp")
        self.cqhttp_popen = subprocess.Popen(
            "cd ./go-cqhttp/;./go-cqhttp -faststart",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        self.gocq_thread = threading.Thread(target=self.display_cqhttp_logger)
        self.gocq_thread.start()

    def start(self):
        self.bot.on_websocket_connection(self.on_websocket_connection)
        self.bot.on_message(self.handle_message)
        self.bot.run(host="127.0.0.1", port=8192)
        # self.bot.get_stranger_info()
    # @bot.on_message

    async def handle_message(self, event: Event):
        if self.group_mode:
            # console.print(event)
            if event["message_type"] == "group":
                # console.print(new_messages)
                if event["group_id"] == self.selected_session:
                    self.new_messages[event["group_id"]] = 0
                    self.ui.add_message(
                        f'[blue][{event["sender"]["card"] or event["sender"]["nickname"]} ({event["sender"]["user_id"]})]:[/]\n {await parser.parser(event["raw_message"], self.bot)}')
                elif event["group_id"] in self.new_messages.keys():
                    self.new_messages[event["group_id"]] += 1
                else:
                    self.new_messages[event["group_id"]] = 1

    async def send_message(self, raw_message):
        # 处理别名
        message = raw_message
        for a in self.aliases["data"]:
            message = message.replace(
                self.aliases["start_with"] + a[0] + self.aliases["end_with"],
                a[1]
            )
        # 执行
        # self.ui.chat.edit(message)
        try:
            await self._send_message(message)
            # self.ui.chat.edit(114514)
        except Exception:
            # self.ui.chat.set_screen("error")
            # self.ui.chat.clean()
            self.ui.chat.edit(traceback.format_exc())
            self.console.print_exception(show_locals=True)

    async def _send_message(self, message):
        command = message.split(" ")
        # self.ui.chat.edit(command)
        if len(message) == 0:
            return None
        elif message[0] == "/":
            if command[0] == "/msg":
                if self.group_mode:
                    await self.bot.send_group_msg(
                        message=message.replace("/msg", "").strip(),
                        group_id=self.selected_session
                    )
                    self.ui.add_message(
                        f'[blue][{self.self_nick} ({self.self_id})]:[/]\n {await parser.parser(message.replace("/msg", "").strip(), self.bot)}'
                    )

            elif command[0] == "/set":
                if command[1] == "group":
                    self.group_mode = True
                    self.selected_session = int(message.split(" ")[2])
                    # self.console.rule(f"Group: {self.select_session}")
                    self.ui.set_group(self.selected_session)
                    history_message = await self.bot.call_action(
                        "get_group_msg_history",
                        group_id=self.selected_session)
                    # 显示历史消息
                    for msg in history_message["messages"]:
                        await self.handle_message(msg)
                else:
                    name = command[1]
                    value = message.replace(f"/set {name}", "").strip()
                    self.aliases["data"] += [[name, value]]
                    json.dump(self.aliases, open("./aliases.json", "w"))

            elif command[0] == "/get":
                if command[1] == "groups":
                    table = rich.table.Table()
                    groups = await self.bot.get_group_list()
                    table.add_column("ID")
                    table.add_column("Name")
                    table.add_column("New")
                    for g in groups:
                        # console.print(g, new_messages)
                        if g["group_id"] not in self.new_messages.keys():
                            self.new_messages[g["group_id"]] = 0
                        table.add_row(str(g["group_id"]), g["group_name"], str(
                            self.new_messages[g["group_id"]]))
                    self.ui.update_groups_list(table)

        elif self.group_mode:
            await self.bot.send_group_msg(
                message=message,
                group_id=self.selected_session
            )
            self.ui.add_message(
                f'[blue][{self.self_nick} ({self.self_id})]:[/]\n {await parser.parser(message, self.bot)}')
    # @bot.on_startup

    async def update_group_list(self):
        while True:
            if self.group_mode:
                await self.send_message("/get groups")
            await asyncio.sleep(1)

    async def update_status(self):
        while True:
            # Mode
            if self.group_mode:
                mode = "Group"
            else:
                mode = "Private"
            # session
            if not self.selected_session:
                session_name = "None"
            elif self.group_mode:
                session_name = (
                    await self.bot.get_group_info(
                        group_id=self.selected_session)
                )["group_name"]
            else:
                session_name = (
                    await self.bot.get_stranger_info(
                        user_id=self.selected_session)
                )["nickname"]

            # 整合文字
            text = f"""User: {self.self_nick} ({self.self_id})
Mode: {mode}
Session: {session_name} ({self.selected_session})"""
            # 渲染
            self.ui.user.update(text)
            # 等待
            await asyncio.sleep(1)

    async def on_websocket_connection(self, event):
        self.console.rule("QCLI (By XiaoDeng3386)")
        self.ui.set_send_func(self.send_message)
        parser.set_send_func(self.send_message)
        asyncio.create_task(self.ui.run_async())
        asyncio.create_task(self.update_group_list())
        asyncio.create_task(self.update_status())
        self.self_nick = (await self.bot.get_login_info())["nickname"]
        self.self_id = (await self.bot.get_login_info())["user_id"]
        # await self.send_message("/get groups")
        #    await asyncio.sleep(5)
        #    groups = await bot.get_group_list()
        #    console.print(groups)
        #    group = True
        #    select_session = console.input("Group: ")


app_class = qCli()
app_class.start()
# threading.Thread(target=send_message).start()
# bot.run(host="127.0.0.1", port=8192)
