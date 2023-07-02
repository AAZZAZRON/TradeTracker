import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import scraping
import utils
import time
import db_tools


def run_discord_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)


    # Event: on_ready
    @client.event
    async def on_ready():
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
                await message.channel.send("Channel already subscribed. No changes made.")
        elif message.content == "!unsubscribechannel":  # remove channel from getting the updates
            if not message.author.guild_permissions.administrator:
                await message.channel.send("You don't have permission to do that!")
                return
            if db_tools.removeChannel(message.channel.id):
                await message.channel.send(f"Channel **{message.channel.id}** unsubscrubed!")
            else:
                await message.channel.send("Channel is not subscribed to updates. No changes made.")


    # scrape 5 minutes
    @tasks.loop(minutes=5)
    async def get_trades_and_signings():
        # get all subscribed channels
        channels = db_tools.getChannels() # or [1125077670816919612]
        removed = 0

        # trades
        for trade in scraping.get_trades():
            embed = utils.create_trade_embed(trade)
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
            time.sleep(1)

        # signings
        for signing in scraping.get_signings():
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
            time.sleep(1)
        

    client.run(TOKEN)
