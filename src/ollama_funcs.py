import asyncio
import os
from ollama import Client, chat


async def StaicyChat( _message):
    response = await asyncio.to_thread(
        chat,
        model="Staicy",
        messages=[{'role': 'user', 'content': _message.content}]
    )
    return response
