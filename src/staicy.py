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
from googleapiclient.discovery import build

import prompts
import ollama_funcs
import helper_funcs as hf

load_dotenv()
chat_session_current = []
#set some variables for ollama
session_file = Path("session.chat")
chat_session_current = hf.load_from_file("session.chat")

    

#get api keys
bot_token = os.getenv("BOT_TOKEN")
staicy_id = os.getenv("STAICY_ID")
creator_id = os.getenv("CREATOR_ID")
search_key = os.getenv("SEARCH_API_KEY")
cse_id = os.getenv("CSE_ID")

service = build("customsearch", "v1", developerKey=search_key)

def google_search(search_term, **kwargs):
    res = service.cse().list(q=search_term, cx=cse_id, num=1, **kwargs).execute()
    return res['items']



status = botfuncs.command_set_activity()

intents = discord.Intents.default()
intents.message_content = True
intents.emojis = True
intents.emojis_and_stickers = True
bot = commands.Bot(command_prefix='S!', intents=intents, activity=status, filter=1, status=discord.Status.online)

def StaicyStart():
    client = Client()
    response = client.create(
        model="Staicy",
        from_="gemma3n:e2b",
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
        or bot.user in message.mentions:
        #reply = ollama_funcs.StaicyChat(message)
        msg = message.content.replace(f"<@{staicy_id}>", "")
        chat_session_current.append({'role': 'user', 'name': message.author.global_name, 'content': msg})
        response = await asyncio.to_thread(
        chat,
        model="Staicy",
        messages=chat_session_current)
        await message.reply(response['message']['content'], mention_author=True)
        chat_session_current.append({'role': 'assistant', 'content': response['message']['content']})
        if len(chat_session_current) > 128:
            chat_session_current.pop(0)
        hf.save_to_file("session.chat", chat_session_current)

    if True:
        response = await asyncio.to_thread(
        chat,
        model="Staicy",
        messages=[{'role': 'system', 'content': "reply only with the first unicode emoji the following message makes you think of and nothing else:"}, {'role': 'user', 'name': message.author.global_name, 'content': message.content}]
        )
        await message.add_reaction(response['message']['content'])
        
    #basic ass commands
    if "S!" in message.content:
        if "time" in message.content:
            current_time = datetime.datetime.now()
            await message.reply(f"It is currently {current_time.strftime('%H:%M')} on {current_time.strftime('%m/%d/%Y')}")

    
        if "guide" in message.content:
            await message.reply(prompts.guide, mention_author=True)

    
        if "ping" in message.content:
            await message.reply('pong', mention_author=True)

    
        if "status" in message.content and message.author.global_name == "Lukan":
            status = message.content.replace("S!", "").replace("status", "")
            await message.reply(status)
            activity = discord.CustomActivity(name=status, emoji='', type=discord.ActivityType.custom)
            await bot.change_presence(activity=activity)
                
        if "search" in message.content:
            query = message.content.replace("S!", "").replace("search", "")
            results = google_search(query)
            for result in results:
                await message.reply(f"Here's what I found:  {result['title']}  [source]({result['link']})", mention_author=True)

        if "redact" in message.content and message.author.global_name == "Lukan":
            msg_id = message.content.replace("S!", "").replace("redact", "")
            message.channel.fetch_message(msg_id)

        if "cease" in message.content and message.author.global_name == "Lukan":
            exit(69)
            
    
        '''
1415812147744735252

'''

StaicyStart()
bot.run(bot_token)
