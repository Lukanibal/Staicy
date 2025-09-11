import asyncio
import json
import os
import discord
import bot_functions as botfuncs
import datetime
import atexit
from dotenv import load_dotenv
from pathlib import Path
from discord.ext import commands
from ollama import Client, chat

import prompts
import ollama_funcs
import helper_funcs as hf

load_dotenv()
chat_session_current = []
#set some variables for ollama
session_file = Path("session.chat")
chat_session_current = hf.load_from_file("session.chat")

    

#Setup the discord bot
bot_token = os.getenv("BOT_TOKEN")
staicy_id = os.getenv("STAICY_ID")
creator_id = os.getenv("CREATOR_ID")
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


@bot.event 
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
    current_message = {'role': 'user', 'content': message.content}
    #her basic llm/chat response stuff is here
    if not "S!" in message.content and f"<@{staicy_id}>" in message.content \
        or message.author.id == creator_id and f"Staicy" in message.content:
        #reply = ollama_funcs.StaicyChat(message)
        chat_session_current.append({'role': 'user', 'name': message.author.global_name, 'content': message.content});
        response = await asyncio.to_thread(
        chat,
        model="Staicy",
        messages=chat_session_current)
        await message.reply(response['message']['content'], mention_author=True)
        chat_session_current.append({'role': 'assistant', 'content': response['message']['content']})
        if len(chat_session_current) > 128:
            chat_session_current.pop(0)
        hf.save_to_file("session.chat", chat_session_current)
        
        
    if "S!" in message.content:
        if "time" in message.content:
            current_time = datetime.datetime.now()
            await message.reply(f"It is currently {current_time.strftime('%H:%M')} on {current_time.strftime('%m/%d/%Y')}")

    if "S!" in message.content:
        if "guide" in message.content:
            await message.reply(prompts.guide, mention_author=True)

    if "S!" in message.content:
        if "ping" in message.content:
            await message.reply('pong', mention_author=True)

    if "S!" in message.content:
        if "ident" in message.content:
            await message.reply(message.author.global_name, mention_author=True)

StaicyStart()
bot.run(bot_token)
