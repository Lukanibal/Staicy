import requests
import json
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
# ComfyUI server URL
comfy_url = "http://127.0.0.1:8188"
prompt_url = f"{comfy_url}/prompt"
comfy_path = os.getenv('COMFY_PATH')

#saves text to file
async def SaveOutput( _text: str, filename: str = "text.txt"):
    with open(f'{comfy_path}/input/{filename}', 'w') as file:
        file.write(_text)



# this should be in the root of the project, 
# mine is included, but not all files may be!
def ProcessTTS(workload: str = "Staicy.json"):
    with open(workload, "r") as f:
        workflow = json.load(f)

    # Define the payload
    payload = {
        "prompt": workflow  # Optional, can be generated
    }
    # Send the request
    response = requests.post(prompt_url, json=payload)

    # Check the response
    if response.status_code == 200:
        id = response.json()["prompt_id"]
        print("Request successful:", id)
        return id
    else:
        print("Error:", response.status_code, response.text)


        

async def check_comfyui_api(job_id):
    url = f"http://localhost:8188/history/{job_id}"  # Adjust the URL as needed
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"{data}")
                    # Check for the condition in the response data
                    if data != {}:  # Replace with the actual condition
                        #async attack to previous message
                        print("Job is done! Exiting loop.")
                        break
                    else:
                        print(f"Current status: {data.get('status')}. Checking again...")
                else:
                    print(f"Error: Received status code {response.status}")
            
            # Wait for a specified interval before checking again
            await asyncio.sleep(5)  # Check every 5 seconds
