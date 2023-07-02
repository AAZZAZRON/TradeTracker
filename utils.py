import discord

def create_trade_embed(data):
    embed = discord.Embed()
    embed.title = f'TRADE: {data["date"]}'
    embed.url = data["details"]
    embed.set_thumbnail(url=data["teams"][0]["icon"])

    for team in data["teams"]:
        name = team["name"]
        icon = team["icon"]
        acq = team["acq"]

        value = ""
        for player in acq:
            desc = player["desc"]
            link = player["link"]
            if link:
                value += f"- [{desc}]({link})\n"
            else:
                value += f"- {desc}\n"

        embed.add_field(name=f"{name} Acquire:", value=value, inline=False)
    return embed

