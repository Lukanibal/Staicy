![Staicy's Profile Picture](https://github.com/Lukanibal/Staicy/blob/main/Staicy.png)  
**Staicy**  
-
She's my personal assistant bot.  
She takes the question "Is that A.I.?" and answers it with a resounding "YES!"  
She is still under development as I learn python to make her specifically.  
Here are some tools that help her work:  
She uses [discord.py](https://pypi.org/project/discord.py/) for her discord bits.  
Her `/news` command uses [NewsData.io](https://newsdata.io)  
Her `/search` command uses [Google's custom search api](https://developers.google.com/custom-search)  
Powered by Gemma3:4b via [Ollama](https://github.com/ollama/ollama) and Stable-Diffusion 1.5 via [Comfy UI](https://www.comfy.org/)  
[VibeVoice ComfyUI Nodes](https://github.com/asimogo/vibevoice-comfyui)  

Her Commands so far:
-
`/guide` shows a helpful guide in discord for how to use her.  
`/tts <text>` will make her say what you type using VibeVoice via ComfyUI(not included in this repo, but linked above!)    
`/imagine <prompt>` will have her paint a picture using Stable Diffusion 1.5 via ComfyUI.  
`/search <query>` will search Google and return the top 3 results, embedding the first one.  
`/news <query>` will return the first result for the news query, and embed it.
  
  
Including `(tts)` will make her respond to your message via VibeVoice, which can take some time depending on the setup.  
Includine `(img)` will act the same as the `/imagine` command, but uses your message as tyhe prompt.  
  

A few examples:
-
the `/imagine` command, makes basic AI art, I will not be improving it, and it may not be sold:  
![image.png](https://github.com/Lukanibal/Staicy/blob/main/images/imagine.png)  
  
the `/tts` command, returns a file named `._00001_.mp3`, it overwrites this to save memory:  
![image.png](https://github.com/Lukanibal/Staicy/blob/main/images/tts.png)  
  
the `/search` command in action:  
![image.png](https://github.com/Lukanibal/Staicy/blob/main/images/search.png)  
