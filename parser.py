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


async def at(message, bot):
    if message.find("CQ:at") == -1:
        return message
    else:
        qq = get_center(message, start="[CQ:at,qq=", end="]")
        nickname = (await bot.get_stranger_info(user_id=qq))["nickname"]
        return await at(message.replace(f"[CQ:at,qq={qq}]", f"[yellow]@{nickname}[/]"), bot)
