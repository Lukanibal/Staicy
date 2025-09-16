import asyncio
import json
import os
import discord
import requests
import bot_functions as botfuncs
import datetime
from discord import app_commands
from dotenv import load_dotenv
from pathlib import Path
from discord.ext import commands
from ollama import Client, chat
import dateparser
import emoji as e
from ltts import SaveOutput, ProcessTTS, check_comfyui_api

import discord_command_funcs as dcf

import prompts
import helper_funcs as hf

load_dotenv()

#=============================================#
##################CHAT VARS####################
#=============================================#
chat_session_current = []
session_file = Path("session.chat")
chat_session_current = hf.load_from_file("session.chat")

#=============================================#
##################API SETUP####################
#=============================================#
bot_token = os.getenv("BOT_TOKEN")
staicy_id = os.getenv("STAICY_ID")
lukan_id = int(os.getenv("LUKAN_ID"))
tts_output_path = os.getenv("TTS_OUTPUT_PATH")
img_output_path = os.getenv("IMG_OUTPUT_PATH")



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




bot = Staicy()

def StaicyStart():
    client = Client()
    response = client.create(
        model="Staicy",
        from_="gemma3:4b",
        system=prompts.system_prompt,
        stream=False,
    )
    print(f"# Client: {response.status}")

#unloads the llma from memory for other processes to grab vram
async def StaicyStop():
    response = await asyncio.to_thread(
            chat,
            model="Staicy",
            keep_alive=0)


#=============================================#
##################COMMANDS#####################
#=============================================#
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

@bot.tree.command(name="tts", description="Have Staicy's beautiful voice regale you with whatever you please")
async def ltts(interaction: discord.Interaction, text: str):
    await interaction.response.defer(thinking=True)
    await SaveOutput(e.replace_emoji(text, ""))
    job_id = ProcessTTS()
    if job_id == -1:
        await interaction.followup.send(f"Sorry, {interaction.user.mention}, but my Text-To-Speech services are currently offline.")
        return
    await check_comfyui_api(job_id)
    await interaction.followup.send(f"{interaction.user.mention}: {text}", file=discord.File(tts_output_path))
    os.remove(tts_output_path)
    
@bot.tree.command(name="greet", description="Greet a user")
async def greet(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"Hello, {user.mention}!")

@bot.tree.command(name="redact", description="Redacts a message that Staicy's sent, only for emergencies!")
async def redact(interaction: discord.Interaction, id: str):
    await interaction.response.defer(thinking=False)
    if interaction.user.id == lukan_id:
        message = await interaction.channel.fetch_message(id)
        await message.delete()
        await interaction.followup.send("Done!")
    else:
        await interaction.followup.send("I only redact things for Mr.Lukan!")

@bot.tree.command(name="obliviate", description="Does what it says on the tin, obliviates her.")
async def obliviate(interaction: discord.Interaction):
    if interaction.user.id == lukan_id:
        chat_session_current.clear()
        await interaction.response.send_message("Huh?")
    else:
        await interaction.response.send_message("Stupefy!")

@bot.tree.command(name="search", description="Staicy will do a quick websearch for you via Google!")
async def search(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)
    
    answer = await hf.google_search(query)
        
    await interaction.followup.send(f"Alright, {interaction.user.mention}, this is what I found:\r\n{answer}")

@bot.tree.command(name="news", description="Staicy will share the current affairs")
async def news(interaction: discord.Interaction, query: str, country: str = "us"):
    await interaction.response.defer(thinking=True)
    
    answer = await hf.get_news(query, country)
        
    await interaction.followup.send(f"Alright, {interaction.user.mention}, this is what I found:\r\n{answer}")

@bot.tree.command(name="status", description="If you're Lukan, this will set her status")
async def status(interaction: discord.Interaction, status: str = ""):
    if interaction.user.id == lukan_id:
        activity = botfuncs.command_set_activity(status)
        await bot.change_presence(activity=activity)
        await interaction.response.send_message(f"New status set!: {activity.name}")
    else:
        await interaction.response.send_message(f"Current status: {activity.name}")

@bot.tree.command(name="cache_refresh", description="If you're Lukan, this will clear her cached messages")
async def CacheRefresh(interaction: discord.Interaction, status: str = "Filed away!"):
    if interaction.user.id== lukan_id:
        chat_session_current.clear()
        await interaction.response.send_message(f"{status}")
    else:
        await interaction.response.send_message(f"Only Mr.Lukan can perform my system commands!")
    
@bot.tree.command(name="imagine", description="make Staicy paint a picture")
async def imagine(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    chunks = await dcf.imagine(interaction, prompt)
    for index, chunk in enumerate(chunks):
        if index == 0:
            await interaction.followup.send(f"{interaction.user.mention}: {prompt}\r\n{chunk}", file=discord.File(img_output_path))
        else:
            await interaction.followup.send(chunk)
    os.remove(img_output_path)

@bot.tree.command(name="schedule", description="Schedule a message with a date and time")
async def schedule(interaction: discord.Interaction, name: str, time: str, date: str):
    if not interaction.user.name == "lukan.spellweaver":
        await interaction.response.send_message("I can only set reminders for Mr.Lukan!")
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

    # hand over info to the function
    delay, formatted = await dcf.schedule(name, time, date)

    if delay is None or -1:
        await interaction.followup.send("I couldn't understand the time you provided. Please try again.")
        return
    if delay == -2:
        await interaction.followup.send("Oh dear, that time's gone by!\r\nCan you please try again with a date and time in the future?")
        return

    await interaction.followup.send(f"Reminder set for {formatted}.")
    # Wait for the specified time
    # todo -- probably not a good thing to just have this command waiting for the set time, probably change it to some time controller
    # like wise because of this current way of doing it, this is probably the best im able to clean up
    await asyncio.sleep(delay)
    # Send the reminder
    await interaction.followup.send(f"{interaction.user.mention}:  {name}")

@bot.tree.command(name="lemons1", description="lemons?")
async def lemons1(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    await SaveOutput(prompts.lemons[0])
    job_id = ProcessTTS()
    if job_id == -1:
        await interaction.followup.send(f"Sorry, {interaction.user.mention}, but my Text-To-Speech services are currently offline.")
        return
    await check_comfyui_api(job_id)
    await interaction.followup.send(f"{interaction.user.mention}: {prompts.lemons[0]}", file=discord.File(tts_output_path))
    os.remove(tts_output_path)

@bot.tree.command(name="lemons2", description="lemons, again?")
async def lemons1(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    await SaveOutput(prompts.lemons[1])
    job_id = ProcessTTS()
    if job_id == -1:
        await interaction.followup.send(f"Sorry, {interaction.user.mention}, but my Text-To-Speech services are currently offline.")
        return
    await check_comfyui_api(job_id)
    await interaction.followup.send(f"{interaction.user.mention}: {prompts.lemons[1]}", file=discord.File(tts_output_path))
    os.remove(tts_output_path)
#=============================================#
##############MESSAGE HANDLING#################
#=============================================#
@bot.event 
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
    
    if bot.user in message.mentions:
        async with message.channel.typing():
            msg = message.content.replace(f"<@{staicy_id}>", "")
            prompt = {'role': 'user', 'name': message.author.global_name, "content": f"This message is from the user {message.author.global_name}: {msg}"}
            if message.attachments:
                # Filter for image attachments
                image_attachments = [attachment for attachment in message.attachments if attachment.content_type and attachment.content_type.startswith('image/')]

                if image_attachments:
                    image_url = image_attachments[0].url
                    # Download the image
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        # Save the image to a file
                        file_path = os.path.join("images", image_attachments[0].filename)  # Specify the directory and filename
                        os.makedirs("images", exist_ok=True)  # Create the directory if it doesn't exist

                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        
                        prompt = {'role': 'user', 'name': message.author.global_name, 'content': f"This message is from the user {message.author.global_name}: {msg}", 'images': [file_path]}
                        
            chat_session_current.append(prompt)
            response = await asyncio.to_thread(
            chat,
            model="Staicy",
            messages=chat_session_current)
            await StaicyStop()

            if "(tts)" in msg:
                await SaveOutput(e.replace_emoji(response['message']['content'], ""))
                job_id = ProcessTTS()
                if job_id == -1:
                    await message.channel.send(f"{response['message']['content']}\r\nSorry, {message.author.mention}, but my Text-To-Speech services are currently offline.")
                    return
                await check_comfyui_api(job_id)
                chunks = await hf.split_string(response['message']['content'])
                for index, chunk in enumerate(chunks):
                    if index == 0:
                        await message.reply(response['message']['content'], mention_author=True, file=discord.File(tts_output_path))
                    else:
                        await message.channel.send(chunk)
                os.remove(tts_output_path)
            
            if "(img)" in msg:
                await SaveOutput(e.replace_emoji(response['message']['content'], ""), "imagetext.txt")
                job_id = ProcessTTS("Painter.json")
                if job_id == -1:
                    await message.channel.send(f"Sorry, {message.author.mention}, but my image generation services are currently offline.")
                    return
                await check_comfyui_api(job_id)
                chunks = await hf.split_string(response['message']['content'])
                for index, chunk in enumerate(chunks):
                    if index == 0:
                        await message.reply(msg.replace("(img)", ""), mention_author=True, file=discord.File(img_output_path))
                    else:
                        await message.channel.send(chunk)
                os.remove(img_output_path)
            
            if "(tts)" not in msg and "(img)" not in msg:
                chunks = await hf.split_string(response['message']['content'])
                for index, chunk in enumerate(chunks):
                    if index == 0:
                        await message.reply(chunk, mention_author=True)
                    else:
                        await message.channel.send(chunk)
                        
        
        chat_session_current.append({'role': 'assistant', 'content': response['message']['content']})
        if len(chat_session_current) > 10:
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
        await StaicyStop()
    
            
                
#=============================================#
##################START BOT####################
#=============================================#
StaicyStart()
bot.run(bot_token)
