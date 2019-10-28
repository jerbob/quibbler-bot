"""A Discord bot to forward messages from quibbler.co."""

import aiohttp
import discord
import socketio

from discord.ext import commands

from bot import constants


bot = commands.Bot(
    command_prefix=">",
    pm_help=False,
    description=__doc__
)
bot.client = socketio.AsyncClient()


@bot.client.event
async def connect():
    print('[?] Connected to quibbler.co')


@bot.client.event
async def disconnect():
    print('[!] Disconnected from quibbler.co')


@bot.client.on('new message')
async def on_message(message: dict):
    if message['usertag'] == 'Discord':
        return
    await bot.session.post(
        constants.WEBHOOK,
        data={
            'content': message['msg'],
            'username': message['usertag']
        }
    )


@bot.client.on('user count')
async def on_user_count(count):
    await bot.channel.edit(topic=f'{count} people in the conversation')


@bot.event
async def on_ready():
    print('[?] Connected to Discord')
    bot.session = aiohttp.ClientSession()
    bot.channel = bot.get_channel(constants.CHANNEL)
    await bot.client.connect(
        f'http://quibbler.co/socket.io/?tag=Discord'
    )


@bot.event
async def on_message(message):
    if message.channel.id == constants.CHANNEL and not message.author.bot:
        name = message.author.display_name
        await bot.client.emit(
            'new message', f'{name}: {message.content}'
        )


bot.run(constants.TOKEN)