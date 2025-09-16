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


async def imagine(interaction, prompt: str):
    await SaveOutput(prompt, "imagetext.txt")
    job_id = ProcessTTS("Painter.json")
    if job_id == -1:
        await interaction.followup.send(f"Sorry, {interaction.user.mention}, but my image generation services are currently offline.")
        return
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