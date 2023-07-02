import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import scraping


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

        if message.content == 'ping':
            await message.channel.send('pong')

    @tasks.loop(minutes=1)
    async def get_trades_and_signings():
        scraping.get_trades()
        


    client.run(TOKEN)
