import discord
from app import get_data, set_file, set_status
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
async def check_status(user, client):
    for guild in client.guilds:
        member = guild.get_member_named(user)
        parse_act(member)
        return

def parse_act(user):    
    act = user.activities
    d = dict()
    for i, activity in enumerate(act):
        d[i] = dict()
        if isinstance(activity, discord.Spotify):
            d[i]["type"] = "listening"
            d[i]["name"] = activity.name
            d[i]["artist"] = activity.artist
            d[i]["album"] = activity.album 
            d[i]["albumCoverUrl"] = activity.album_cover_url
            d[i]["title"] = activity.title 
            d[i]["trackID"] = activity.track_id
            d[i]["trackUrl"] = activity.track_url
            d[i]["startedAt"] = activity.created_at.strftime("%I:%M %p")
        else:
            d[i]["name"] = activity.name
            d[i]["url"] = activity.url
            d[i]["timeStamps"] = activity.timestamps
            d[i]["state"] = activity.state
            d[i]["type"] = activity.type[0] if isinstance(activity.type, list) else "None"
            d[i]["details"] = activity.details
            d[i]["assets"] = activity.assets
            
    set_status(d)

#Client events -------
@client.event
async def on_ready() -> None: #When bot starts up, adds log
    print("Bot is ready to party, logged in as {0.user}.".format(client))
    discord_activity = watched_user #Displays bot's activity
    await check_status(watched_user, client)
    await client.change_presence(activity=discord.Activity(type = discord.ActivityType.listening, name = discord_activity))
    return

@client.event
async def on_message(message) -> None: #On every incoming message, run the below code
  author = str(message.author)
  if message.author == client.user: #If message sender is another bot, or itself, or a non-user
    return 
  elif message.content.lower().startswith('!dm test'): #Message is sent with designated prefix, !df by default
    await message.channel.send("Testing!")
@client.event
async def on_presence_update(before, after): 
    if str(after) == watched_user:
        parse_act(after)




if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
