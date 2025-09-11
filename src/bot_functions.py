import discord
import random


#the base of this is copied from flukebot, thanks evan
def command_set_activity(current_activity=None):
    possible_activities = [
        discord.Game(name="Papers, Please", platform="steam", type=discord.ActivityType.playing),
        discord.Activity(type=discord.ActivityType.listening, name='Korn - Twisted Transistor'),
        discord.Activity(type=discord.ActivityType.watching, name="KPop Demon Hunters"),
        discord.CustomActivity(name="Filing", emoji='🗃️'),
        discord.CustomActivity(name="Assisting in any way I can", emoji='☑️'),
        None  # Clear status
    ]

    # Remove the current activity from the list if it matches
    if current_activity in possible_activities:
        possible_activities.remove(current_activity)

    # Pick a new one randomly from the rest
    return random.choice(possible_activities)