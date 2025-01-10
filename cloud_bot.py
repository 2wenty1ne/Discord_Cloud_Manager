import os
import discord
import random
from discord.ext import commands
from datetime import datetime, timedelta
from dotenv import load_dotenv

from public_transport import Public_transportView

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TEST_CHANNEL_ID = int(os.getenv('TEST_CHANNEL_ID'))
bot_description = "Kein Sex vor der E"


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


def activity_decider():
    activity_one = discord.Activity(type=discord.ActivityType.watching, name=f'your naked mum | Prefix: {prefix}')
    activity_two = discord.Activity(type=discord.ActivityType.listening, name=f'your mum moaning | Prefix: {prefix}')
    return random.choice([activity_one, activity_two])


@bot.event
async def on_ready():
    await bot.change_presence(activity=activity_decider())
    await send_message("Start", f'{bot.user} is ready!', switch="server", channel=TEST_CHANNEL_ID)
    print(f'Discord Managment Bot ready!')


@bot.command()
async def msg(ctx, *args):
    response = " ".join(args) if args else "empty :("
    await send_message(f"Message from: {ctx.author}", response, "server", channel=ctx.channel.id)


@bot.command()
async def new_pt(ctx, *args):
    if not args:
        await send_message("Time missing", f"You need to provide the time the transport vehicle departs!\n Use this format: HH:MM\nExample: **{prefix}new_pt 13:37**", "server", channel=ctx.channel.id)
        return

    if len(args) > 1:
        departure_reason = ""
        for reason in args[1:]:
            departure_reason = f'{departure_reason} {reason}'
        departure_reason = f'{departure_reason} -'
    else:
        departure_reason = "Your"

    arg = args[0]

    if not validate_times(arg):
        await send_message("Invalid time format!", f"Use this format: HH:MM\nExample: **{prefix}new_pt 13:37**", "server", channel=ctx.channel.id)
        return

    await ctx.message.delete()

    departure_time = datetime.strptime(arg, "%H:%M")
    embed_title = "New public transport"
    embed_description = "Do you want to take a shower?"
    await send_message(embed_title, embed_description, "server", channel=ctx.channel.id, view=Public_transportView(departure_time, departure_reason))



bot.run(TOKEN)