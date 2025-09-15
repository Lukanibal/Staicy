import discord
import random
 

def command_set_activity(name : str = ""):
    possible_activities = [
        discord.Game(name="Papers, Please", platform="steam", type=discord.ActivityType.playing),
        discord.Activity(type=discord.ActivityType.listening, name='KoЯn - Twisted Transistor'),
        discord.Activity(type=discord.ActivityType.listening, name='Scissor Sisters - I Can\'t Decide'),
        discord.Activity(type=discord.ActivityType.listening, name='Shania Twain - Man! I Feel Like a Woman!'),
        discord.Activity(type=discord.ActivityType.watching, name="KPop Demon Hunters"),
        discord.Activity(type=discord.ActivityType.watching, name="Court TV - Judge Judy"),
        discord.Activity(type=discord.ActivityType.listening, name="Magdalena Bay - Money Lover"),
        discord.Activity(type=discord.ActivityType.listening, name="Caroline Polachek - So Hot You're Hurting My Feelings"),
        discord.CustomActivity(name="Filing", emoji='🗃️'),
        discord.CustomActivity(name="Assisting in any way I can", emoji='☑️'),
    ]

    # Remove the current activity from the list if it matches

    if name == "":
        return random.choice(possible_activities)
    else:
        return discord.CustomActivity(name=name, emoji='')