import discord
from app import get_data, set_file, set_status
from datetime import datetime

VALUES = get_data("values")
DISCORD_TOKEN : str = VALUES["discordToken"]
watched_user : list[str] = VALUES["watchedUser"]


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
    d["currentStatus"] = dict()
    for activity in act:
        if isinstance(activity, discord.Spotify):
            d["currentStatus"]["spotifyArtist"] = activity.artist if hasattr(activity, "artist") else None
            d["currentStatus"]["spotifyAlbum"] = activity.album if hasattr(activity, "album") else None 
            d["currentStatus"]["spotifyAlbumCoverUrl"] = activity.album_cover_url if hasattr(activity, "album_cover_url") else None
            d["currentStatus"]["spotifyTitle"] = activity.title if hasattr(activity, "title") else None
            d["currentStatus"]["spotifyTrackUrl"] = activity.track_url if hasattr(activity, "track_url") else None
        else:
            d["currentStatus"]["activityName"] = activity.name if hasattr(activity, "name") else None
            d["currentStatus"]["activityUrl"] = activity.url if hasattr(activity, "url") else None
            d["currentStatus"]["activityState"] = activity.state if hasattr(activity, "state") else None
            try:
                d["currentStatus"]["activityType"] = activity.type[0] if hasattr(activity, "type") else None
            except:
                pass
            d["currentStatus"]["activityDetails"] = activity.details if hasattr(activity, "details") else None
            
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
