'''
sets up discord bot + commands (on message + task.loop())
'''

import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import scraping
import utils
import db_tools
from datetime import datetime
import pytz
import asyncio
import nest_asyncio

nest_asyncio.apply()


<<<<<<< HEAD
def run_discord_bot():
=======
def run_discord_bot(): 
  # set up discord client
>>>>>>> f6e7050a1b6f8ad4d8c1bf3dacb544d364a9cc1b
  load_dotenv()
  TOKEN = os.getenv('DISCORD_TOKEN')

  intents = discord.Intents.default()
  intents.message_content = True
  client = discord.Client(intents=intents)

  # Event: on_ready
  @client.event
  async def on_ready():
    # db_tools.init_db()  # remove keys from previous runs
    await client.get_channel(1125077670816919612).send(f'{client.user} is now running!')
    print(f'{client.user} is now running!')
    get_trades_and_signings.start()

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
      else:
        await message.channel.send(
          "Channel already subscribed. No changes made.")
    elif message.content == "!unsubscribechannel":  # remove channel from getting the updates
      if not message.author.guild_permissions.administrator:
        await message.channel.send("You don't have permission to do that!")
        return
      if db_tools.removeChannel(message.channel.id):
        await message.channel.send(f"Channel **{message.channel.id}** unsubscrubed!")
      else:
        await message.channel.send("Channel is not subscribed to updates. No changes made.")

  # ----------------------- SCRAPING ----------------------- #

  async def send_trade_embeds():
    print("get trades")
    # get all subscribed channels
    channels = db_tools.getChannels()  # or [1125077670816919612]
    removed = 0

    # get the trades
    coro = asyncio.to_thread(scraping.get_trades)
    trades = await coro

    check = db_tools.getLastTradeShown()  # last one displayed
    db_tools.setLastTradeShown(trades[0])
    print(trades[0])

    for trade in trades:
      if check == None or check == trade:  # if trade is equal to last one displayed (as per db)
        break
      embed = utils.create_trade_embed(trade) # create embed
      if removed:
        channels = db_tools.getChannels()
        removed = 0
      for channel in channels:
        try:
          await client.get_channel(channel).send(embed=embed)
        except AttributeError:  # if channel is deleted
          print(f"Channel {channel} not found. Removing from db.")
          db_tools.removeChannel(channel)
          removed = 1
      await asyncio.sleep(1)

  async def send_signing_embeds():
    print("get signings")
    # get all subscribed channels
    channels = db_tools.getChannels()  # or [1125077670816919612]
    removed = 0

    # signings
    coro = asyncio.to_thread(scraping.get_signings)
    signings = await coro

    check = db_tools.getLastSigningShown()
    db_tools.setLastSigningShown(signings[0])
    print(signings[0])

    for signing in signings:
      if check == None or check == signing:
        break
      embed = utils.create_signing_embed(signing)
      if removed:
        channels = db_tools.getChannels()
        removed = 0
      for channel in channels:
        try:
          await client.get_channel(channel).send(embed=embed)
        except AttributeError:
          print(f"Channel {channel} not found. Removing from db.")
          db_tools.removeChannel(channel)
          removed = 1
      await asyncio.sleep(1)

  # scrape every x minutes
  @tasks.loop(minutes=20)
  async def get_trades_and_signings():
    try:
      # start scraping
      tz_NY = pytz.timezone('America/New_York')
      start_time = datetime.now(tz_NY)
      await client.get_channel(1125077670816919612).send(f"**{start_time.strftime('%H:%M:%S')}**: Scraping...")

      # actual scraping part
      asyncio.run(send_trade_embeds())
      asyncio.run(send_signing_embeds())


      # end scraping
      tz_NY = pytz.timezone('America/New_York')
      end_time = datetime.now(tz_NY)
      await client.get_channel(1125077670816919612).send(
        f"**{end_time.strftime('%H:%M:%S')}**: Done scraping. Time spent: **{end_time - start_time}**"
      )

    except Exception as e:
      await client.get_channel(1125077670816919612).send(
        f"<@515698891673305089> an error occurred: `{e}`")

  client.run(TOKEN)
