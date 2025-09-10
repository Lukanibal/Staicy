import asyncio
import discord
from pathlib import Path
from discord.ext import commands

from ollama import Client, chat


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run('token')
