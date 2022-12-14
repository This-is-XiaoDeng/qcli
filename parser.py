def get_center(text, start, end, start_search=0):
    start_len = text.find(start, start_search)
    if start_len == -1:
        return None
    else:
        end_len = text.find(end, start_len)
        if end_len == -1:
            return None
        else:
            return text[start_len + len(start):end_len]


async def image(message):
    if message.find("CQ:image") == -1:
        return message
    else:
        data = get_center(message, "[CQ:image", "]")
        return await image(message.replace(f"[CQ:image{data}]", "[yellow][Image][/]"))


async def at(message, bot):
    if message.find("[CQ:at") == -1:
        return message
    else:
        qq = get_center(message, start="[CQ:at,qq=", end="]")
        nickname = (await bot.get_stranger_info(user_id=qq))["nickname"]
        return await at(message.replace(f"[CQ:at,qq={qq}]", f"[yellow]@{nickname}[/]"), bot)


async def reply(message, bot):
    if message.find("CQ:reply") == -1:
        return message
    else:
        id = get_center(message, "[CQ:reply,id=", "]")
        reply_message = await bot.get_msg(message_id=int(id))
    return await reply(message.replace(f"[CQ:reply,id={id}]", f"[green][Re: {reply_message['sender']['nickname']}: {reply_message['message']}][/]\n"), bot)


async def parser(message, bot):
    msg = message

    msg = await reply(msg, bot)
    msg = await at(msg, bot)
    msg = await image(msg)
    return msg
