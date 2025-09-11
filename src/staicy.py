import asyncio
import json
import os
import discord
import bot_functions as botfuncs
import datetime
from dotenv import load_dotenv
from pathlib import Path
from discord.ext import commands
from ollama import Client, chat

import prompts
import ollama_funcs

load_dotenv()

#set some variables for ollama
chat_session_current = []

#Setup the discord bot
bot_token = os.getenv("BOT_TOKEN")
status = botfuncs.command_set_activity()

intents = discord.Intents.default()
intents.message_content = True
intents.emojis = True
intents.emojis_and_stickers = True
bot = commands.Bot(command_prefix='S!', intents=intents, activity=status, status=discord.Status.online)

def StaicyStart():
    client = Client()
    response = client.create(
        model="Staicy",
        from_="gemma3",
        system=prompts.system_prompt,
        stream=False,
    )
    print(f"# Client: {response.status}")

#some very basic bot commands
@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def time(ctx):
    current_time = datetime.datetime.now()
    await ctx.send(f"It is currently {current_time.strftime('%H:%M')} on {current_time.strftime('%m/%d/%Y')}")

@bot.command()
async def guide(ctx):
    await ctx.send(prompts.guide)

@bot.event 
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    if not "S!" in message.content:
        #reply = ollama_funcs.StaicyChat(message)
        response = await asyncio.to_thread(
        chat,
        model="Staicy",
        messages=[{'role': 'user', 'content': message.content}])
        await message.reply(response['message']['content'], mention_author=True)

StaicyStart()
bot.run(bot_token)
