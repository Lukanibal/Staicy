import asyncio
import json
import os
import discord
import bot_functions as botfuncs
import datetime
from discord import app_commands
from dotenv import load_dotenv
from pathlib import Path
from discord.ext import commands
from ollama import Client, chat
from googleapiclient.discovery import build
import dateparser
import emoji as e

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

#google api setup
service = build("customsearch", "v1", developerKey=search_key)

async def google_search(search_term, **kwargs):
    res = service.cse().list(q=search_term, cx=cse_id, num=3, filter=1, **kwargs).execute()
    results = res['items']
    answer = ""
    for result in results:
        answer += f"{result['title']}  [source](<{result['link']}>)"
    return answer
    

class Staicy(discord.Client):
    def __init__(self):
        status = botfuncs.command_set_activity()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.emojis = True
        intents.emojis_and_stickers = True
        super().__init__(intents=intents, activity=status)
        self.tree = app_commands.CommandTree(self)
        self.synced=False

    async def setup_hook(self):
        #put em here
        pass

    async def on_ready(self):
        if self.synced:
            return
        for guild in self.guilds:
            guild_obj = discord.Object(id=guild.id)
            self.tree.copy_global_to(guild=guild_obj)
            await self.tree.sync(guild=guild_obj)
        self.synced = True
        print(f"Synced to {len(self.guilds)} guilds")






bot = Staicy()#commands.Bot(command_prefix='S!', intents=intents, activity=status, status=discord.Status.online)

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

@bot.tree.command(name="ping", description="She'll pong ya!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('pong!')


@bot.tree.command(name="time", description="returns the current time in Lukan's timezone(PST/PDT)")
async def time(interaction: discord.Interaction):
    current_time = datetime.datetime.now()
    await interaction.response.send_message(f"It is currently {current_time.strftime('%H:%M')} on {current_time.strftime('%m/%d/%Y')}")

@bot.tree.command(name="guide", description="Shows Staicy's guide, for helpful tips!")
async def guide(interaction: discord.Interaction):
    await interaction.response.send_message(prompts.guide)


@bot.tree.command(name="greet", description="Greet a user")
async def greet(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"Hello, {user.mention}!")


@bot.tree.command(name="search", description="Staicy will do a quick websearch for you via Google!")
async def search(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)
    
    answer = await google_search(query)
        
    await interaction.followup.send(f"Alright, {interaction.user.mention}, this is what I found:\r\n{answer}")

@bot.tree.command(name="status", description="If you're Lukan, this will set her status")
async def status(interaction: discord.Interaction, status: str):
    if interaction.user.name == "lukan.spellweaver":
        activity = discord.CustomActivity(name=status, emoji='', type=discord.ActivityType.custom)
        await bot.change_presence(activity=activity)
        await interaction.response.send_message(f"New status set: {status}")
    else:
        await interaction.response.send_message(f"Current status: {bot.activity}")
    

@bot.tree.command(name="schedule", description="Schedule a message with a date and time")
async def schedule(interaction: discord.Interaction, name: str, time: str, date: str):
    if not interaction.user.name == "lukan.spellweaver":
        await interaction.response.send_message("I can only set reminders for Lukan!")
        return
    await interaction.response.defer(thinking=True)
    # Extract the date and time
    reminder_time = dateparser.parse(time)
    if reminder_time is None:
        await interaction.followup.send("I couldn't understand the time you provided. Please try again.")
        return
    now = datetime.datetime.now()
    if reminder_time < now:
        await interaction.followup.send("Oh dear, that time's gone by!\r\nCan you please try again with a date and time in the future?")
        return
    delay = (reminder_time - now).total_seconds()
    await interaction.followup.send(f"Reminder set for {reminder_time.strftime('%Y-%m-%d %I:%M %p')}.")

    # Wait for the specified time
    await asyncio.sleep(delay)
    # Send the reminder
    await interaction.followup.send(f"{interaction.user.mention}:  {name}")

@bot.event 
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        #reply = ollama_funcs.StaicyChat(message)
        msg = message.content.replace(f"<@{staicy_id}>", "")
        chat_session_current.append({'role': 'user', 'name': message.author.global_name, 'content': msg})
        response = await asyncio.to_thread(
        chat,
        model="Staicy",
        messages=chat_session_current)
        await message.reply(response['message']['content'], mention_author=True)
        chat_session_current.append({'role': 'assistant', 'content': response['message']['content']})
        if len(chat_session_current) > 20:
            chat_session_current.pop(0)
        hf.save_to_file("session.chat", chat_session_current)

    if True:
        response = await asyncio.to_thread(
        chat,
        model="Staicy",
        messages=[{'role': 'system', 'content': "reply only with the first unicode emoji the following message makes you think of and nothing else:"}, {'role': 'user', 'name': message.author.global_name, 'content': message.content}]
        )
        emote = e.distinct_emoji_list(response['message']['content'])

        await message.add_reaction(emote[0])
    
            
                

StaicyStart()
bot.run(bot_token)
