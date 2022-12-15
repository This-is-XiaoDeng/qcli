from aiocqhttp import CQHttp
import parser
import asyncio
from aiocqhttp import Event
import rich.console
import app
import rich.table
import json
import threading
#import os
import subprocess


class qCli():
    config = json.load(open("./config.json"))
    bot = CQHttp(
        api_root=config["go-cqhttp"]["api_root"],
        access_token=config["go-cqhttp"]["access_token"],
        secret=config["go-cqhttp"]["secret"]
    )
    select_seesion = None
    group = True
    ui = app.QCli()
    console = rich.console.Console()
    new_messages = {}
    self_nick = None
    self_id = None
    gocq = None

    def display_gocq_log(self):
        while True:
            buffer = self.gocq.stdout.readline().decode()
            if buffer != "" and self.gocq.poll() != None:
                break
            buffer = buffer[buffer.find(" [")+1:].replace("\n", "")
            if self.self_nick != None:
                self.ui.gocqlog.update(buffer)
            else:
                self.console.print(buffer)

    def __init__(self):
        #self.gocq = os.popen("cd ./go-cqhttp/;./go-cqhttp")
        self.gocq = subprocess.Popen("cd ./go-cqhttp/;./go-cqhttp",
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
        self.gocq_thread = threading.Thread(target=self.display_gocq_log)
        self.gocq_thread.start()

    def start(self):
        self.bot.on_websocket_connection(self.on_startup)
        self.bot.on_message(self.handle_msg)
        self.bot.run(host="127.0.0.1", port=8192)
        # self.bot.get_stranger_info()
    # @bot.on_message

    async def handle_msg(self, event: Event):
        if self.group:
            # console.print(event)
            if event["message_type"] == "group":
                # console.print(new_messages)
                if event["group_id"] == self.select_seesion:
                    self.ui.add_message(
                        f'[blue][{event["sender"]["card"] or event["sender"]["nickname"]} ({event["sender"]["user_id"]})]:[/]\n {await parser.parser(event["raw_message"], self.bot)}')
                elif event["group_id"] in self.new_messages.keys():
                    self.new_messages[event["group_id"]] += 1
                else:
                    self.new_messages[event["group_id"]] = 1

    async def send_message(self, message):
        if len(message) == 0:
            return None
        elif message[0] == "/":
            if message[:4] == "/msg":
                if self.group:
                    await self.bot.send_group_msg(
                        message=message[5:], group_id=self.select_seesion)
                    self.ui.add_message(
                        f'[blue][{self.self_nick} ({self.self_id})]:[/]\n {await parser.parser(message, self.bot)}')

            elif message[:4] == "/set":
                if message.split(" ")[1] == "group":
                    self.group = True
                    self.select_seesion = int(message.split(" ")[2])
                    #self.console.rule(f"Group: {self.select_seesion}")
                    self.ui.set_group(self.select_seesion)
                    history_message = await self.bot.call_action("get_group_msg_history", group_id=self.select_seesion)
                    for msg in history_message["messages"]:
                        await self.handle_msg(msg)
            elif message[:4] == "/get":
                if message.split(" ")[1] == "groups":
                    table = rich.table.Table()
                    groups = await self.bot.get_group_list()
                    table.add_column("ID")
                    table.add_column("Name")
                    table.add_column("New")
                    for g in groups:
                        #console.print(g, new_messages)
                        if g["group_id"] not in self.new_messages.keys():
                            self.new_messages[g["group_id"]] = 0
                        table.add_row(str(g["group_id"]), g["group_name"], str(
                            self.new_messages[g["group_id"]]))
                    self.ui.set_groups_list(table)

        elif self.group:
            await self.bot.send_group_msg(message=message, group_id=self.select_seesion)
            self.ui.add_message(
                f'[blue][{self.self_nick} ({self.self_id})]:[/]\n {await parser.parser(message, self.bot)}')
    # @bot.on_startup

    async def on_startup(self, event):
        self.console.rule("QCLI (By XiaoDeng3386)")
        self.self_nick = (await self.bot.get_login_info())["nickname"]
        self.self_id = (await self.bot.get_login_info())["user_id"]
        self.ui.set_send_func(self.send_message)
        asyncio.create_task(self.ui.run_async())
        await self.send_message("/get groups")
        #    await asyncio.sleep(5)
        #    groups = await bot.get_group_list()
        #    console.print(groups)
        #    group = True
        #    select_seesion = console.input("Group: ")


app_class = qCli()
app_class.start()
# threading.Thread(target=send_message).start()
# bot.run(host="127.0.0.1", port=8192)
