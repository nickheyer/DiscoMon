import discord
from app import get_data, set_file
from datetime import datetime

VALUES = get_data("values")
DISCORD_TOKEN : str = VALUES["discordToken"]
watched_user : list[str] = VALUES["watchedUser"]
delay : int = int(VALUES["delay"])


#Declaring intents, must also be configured from Discord portal, see readme
intents = discord.Intents.all()
intents.members = True

#Discord, Discord-Embed
client = discord.Client(intents = intents)
embeded = discord.Embed()

#Generic Functions -------


#Client events -------

@client.event
async def on_ready() -> None: #When bot starts up, adds log
    print("Bot is ready to party, logged in as {0.user}.".format(client))
    discord_activity = watched_user #Displays bot's activity

    await client.change_presence(activity=discord.Activity(type = discord.ActivityType.listening, name = discord_activity)) 
    return

@client.event
async def on_message(message) -> None: #On every incoming message, run the below code
  if message.author == client.user : #If message sender is another bot, or itself, or a non-user
    return 
  elif message.content.lower().startswith('!dm'):
    await message.channel.send(message.content) #Echo Test
  else:
    return

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
