'''
sets up discord bot + commands (on message + task.loop())
'''

import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from features.signings import send_signing_embeds
from features.trades import send_trade_embeds
import features.scrape_starting_goalies as scrape_starting_goalies
import db_tools
from datetime import datetime
import pytz
import asyncio
import nest_asyncio

nest_asyncio.apply()


def run_discord_bot(): 
  # set up discord client
  load_dotenv()
  TOKEN = os.getenv('DISCORD_TOKEN')
  ADMIN_CHANNEL = int(os.getenv('ADMIN_CHANNEL'))
  ADMIN_ID = os.getenv('ADMIN_ID')

  intents = discord.Intents.default()
  intents.message_content = True
  client = discord.Client(intents=intents)

  # Event: on_ready
  @client.event
  async def on_ready():
    # db_tools.init_db()  # remove keys from previous runs
    await client.get_channel(ADMIN_CHANNEL).send(f'{client.user} is now running!')
    print(f'{client.user} is now running!')
    get_trades_and_signings.start()
    # get_starting_goalies.start()


  # Event: on_message
  @client.event
  async def on_message(message):
    if message.author == client.user:
      return
    if message.content == '!ping':
      await message.channel.send('pong')
    elif message.content == "!subscribechannel":  # add channel to get updates
      if not message.author.guild_permissions.administrator:
        await message.channel.send("You don't have permission to do that!")
        return
      if db_tools.addChannel(message.channel.id):
        await message.channel.send(f"Channel **{message.channel.id}** subscribed to updates.")
        await client.get_channel(ADMIN_CHANNEL).send(f"New channel **{message.channel.id}** subscribed to updates.")
      else:
        await message.channel.send("Channel already subscribed. No changes made.")
    elif message.content == "!unsubscribechannel":  # remove channel from getting the updates
      if not message.author.guild_permissions.administrator:
        await message.channel.send("You don't have permission to do that!")
        return
      if db_tools.removeChannel(message.channel.id):
        await message.channel.send(f"Channel **{message.channel.id}** unsubscrubed!")
        await client.get_channel(ADMIN_CHANNEL).send(f"Channel **{message.channel.id}** unsubscribed to updates.")
      else:
        await message.channel.send("Channel is not subscribed to updates. No changes made.")

  # ----------------------- SCRAPING ----------------------- #

  # scrape every x minutes
  @tasks.loop(minutes=20)
  async def get_trades_and_signings():
    try:
      # start scraping
      tz_NY = pytz.timezone('America/New_York')
      start_time = datetime.now(tz_NY)
      await client.get_channel(ADMIN_CHANNEL).send(f"**{start_time.strftime('%H:%M:%S')}**: Scraping...")

      # actual scraping part
      asyncio.run(send_trade_embeds(client))
      asyncio.run(send_signing_embeds(client))


      # end scraping
      tz_NY = pytz.timezone('America/New_York')
      end_time = datetime.now(tz_NY)
      await client.get_channel(ADMIN_CHANNEL).send(f"**{end_time.strftime('%H:%M:%S')}**: Done scraping. Time spent: **{end_time - start_time}**")

    except Exception as e:
      await client.get_channel(ADMIN_CHANNEL).send(f"<@{ADMIN_ID}> an error occurred: `{e}`")


  @tasks.loop(minutes=20)
  async def get_starting_goalies():
    try:
      # start scraping
      tz_NY = pytz.timezone('America/New_York')
      start_time = datetime.now(tz_NY)
      await client.get_channel(ADMIN_CHANNEL).send(f"**{start_time.strftime('%H:%M:%S')}**: Scraping...")

      # actual scraping part
      scrape_starting_goalies.get_starters()

      # end scraping
      tz_NY = pytz.timezone('America/New_York')
      end_time = datetime.now(tz_NY)
      await client.get_channel(ADMIN_CHANNEL).send(f"**{end_time.strftime('%H:%M:%S')}**: Done scraping. Time spent: **{end_time - start_time}**")

    except Exception as e:
      await client.get_channel(ADMIN_CHANNEL).send(f"<@{ADMIN_ID}> an error occurred: `{e}`")


  client.run(TOKEN)
