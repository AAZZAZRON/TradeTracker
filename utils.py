import discord


def create_trade_embed(data):
  embed = discord.Embed(color=0x50afaa)
  embed.title = f'TRADE: {data["date"]}'
  embed.url = data["details"]
  embed.set_thumbnail(
    url=data["teams"][0]["icon"])  # TODO: merge team icons together

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


def create_signing_embed(data):
  embed = discord.Embed(color=0xe1b51e)
  embed.title = f'SIGNING: {data["player"]["name"]} to {data["team"]["name"]}'
  embed.description = f'{data["date"]}'
  embed.url = data["details"]
  embed.set_thumbnail(url=data["team"]["icon"])

  player = data["player"]
  player_value = f"{player['name']} - {player['position']}\n{player['age']} years old"
  embed.add_field(name="Player: ", value=player_value, inline=False)

  contract = data["contract"]
  contract_value = f"{contract['capHit']} x {contract['length']}\nTotal: {contract['total']}\nType: {contract['type']}"
  embed.add_field(name="Contract: ", value=contract_value, inline=False)

  return embed
