import asyncio
import datetime
import os
import dateparser
from ollama import Client, chat
from dotenv import load_dotenv
import helper_funcs as hf
from ltts import SaveOutput, ProcessTTS, check_comfyui_api

load_dotenv()
img_output_path = os.getenv("IMG_OUTPUT_PATH")

async def schedule(name: str, time: str, date: str):
    reminder_time = dateparser.parse(time)
    if reminder_time is None:
        print("Can not understand time provided")
        return -1
    now = datetime.datetime.now()
    if reminder_time < now:
        print('Time has expired')
        return -2
    delay = (reminder_time - now).total_seconds()
    formated_time = reminder_time.strftime('%Y-%m-%d %I:%M %p')
    return delay, formated_time

async def imagine(interaction, prompt: str):
    await SaveOutput(prompt, "imagetext.txt")
    job_id = ProcessTTS("Painter.json")
    await check_comfyui_api(job_id)
    new_prompt = {'role': 'user', 'name': interaction.user.name,
                  'content': "You just painted this, describe the image and eplain your process",
                  'images': [img_output_path]}
    response = await asyncio.to_thread(
        chat,
        model="Staicy",
        messages=[new_prompt],
        stream=False)
    chunks = await hf.split_string(response['message']['content'])
    return chunks