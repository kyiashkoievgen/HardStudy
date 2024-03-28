import os

import discord  # Подключаем библиотеку
from discord.ext import commands
from dotenv import load_dotenv

from web.hard_study.modls import Language

load_dotenv()
discord_token = os.getenv('DISCORD_KEY')
intents = discord.Intents.default()  # Подключаем "Разрешения"
intents.message_content = True
# Задаём префикс и интенты
bot = commands.Bot(command_prefix='>', intents=intents)


# инициализация бота
@bot.event
async def on_ready():
    languages = set(Language.query.all().name)
    server_channels = set()
    print(f'Бот {bot.user} подключился к Discord!')
    print('------')
    # показать комнаты сервера
    for guild in bot.guilds:
        print(guild.name)
        for channel in guild.text_channels:
            print(channel)
            server_channels.add(channel)
    # если нет комнаты для языка, создать
    for language in languages:
        if language not in server_channels:
            await guild.create_text_channel(language)
            print(f'Создана комната для языка {language}')




# С помощью декоратора создаём первую команду
@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(discord_token)
