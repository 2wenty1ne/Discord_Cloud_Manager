import os
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from dotenv import load_dotenv

from public_transport import Public_transportView

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_TEST')
#TOKEN = os.getenv('DISCORD_TOKEN')
TEST_CHANNEL_ID = int(os.getenv('TEST_CHANNEL_ID_AFFENHAUS'))
bot_description = "Kein Sex vor der E"
pt_time = 0

intents = discord.Intents.all()
prefix = "!"
bot = commands.Bot(command_prefix=prefix, description=bot_description, intents=intents)


async def send_message(dm_title, dm_description, switch, color = None, message=None, channel=None, view=None):
    current_time = datetime.utcnow()
    if color == "error":
        colorpick = discord.Color.from_rgb(255, 38 ,0)
    else:
        colorpick = discord.Color.from_rgb(45, 125 ,70)
    embeded_response = discord.Embed(title=dm_title, description=dm_description, timestamp=current_time, color=colorpick)

    if switch == "server":
        if message == None:
            channel = bot.get_channel(channel)
        else:
            channel = bot.get_channel(message.channel.id)
        send_message = await channel.send(embed=embeded_response, view=view)
    elif switch == "dm":
        dmrecipient = bot.get_user(208685464876482561)
        dmrecipient.create_dm
        send_message = await dmrecipient.send(embed=embeded_response)

    return send_message


def validate_times(time_to_validate):
    try:
        datetime.strptime(time_to_validate, "%H:%M")
        return 1
    except ValueError:
        return 0


@bot.event
async def on_ready():
    await send_message("Start", f'{bot.user} is ready!', switch="server", channel=TEST_CHANNEL_ID)
    print(f'Discord Managment Bot ready!')


@bot.command()
async def new_pt(ctx, arg):
    await ctx.message.delete()
    if not validate_times(arg):
        await ctx.send("Invalid time format, use HH:MM")
        return

    departure_time = datetime.strptime(arg, "%H:%M")
    embed_title = "New public transport"
    embed_description = "Do you want to take a shower?"
    await send_message(embed_title, embed_description, "server", channel=ctx.channel.id, view=Public_transportView(departure_time))



bot.run(TOKEN)