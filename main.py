import discord
import os
from discord import message
import requests
import json
from discord import client
from discord.ext import tasks

client = discord.Client()

fav_list = ''
target_channel_id = int(os.environ.get('CHANNEL_ID'))

def get_schedule():
    lst = []
    url = "https://jikan1.p.rapidapi.com/schedule/sunday"
    headers = {
    'x-rapidapi-host': "jikan1.p.rapidapi.com",
    'x-rapidapi-key': os.environ.get('API_KEY')
    }
    response = requests.request("GET", url, headers=headers)
    txt = json.loads(response.text)
    res = txt['sunday']
    for i in range(0, len(res)):
        final_res=res[i]['title']
        lst.append(final_res)
    return lst

def read_contents():
    shows_list = []
    fav_list = get_schedule()
    with open('favs.txt') as f:
        contents = f.readlines()
    for i in contents:
        new_contents = i.split('\n')[0]
        if new_contents in fav_list:
            shows_list.append(new_contents)
    return shows_list

@client.event
async def on_ready():
    print(f'We up as {client.user}!')

@tasks.loop(minutes=1.0)
async def called_once_a_day():
    message_channel = client.get_channel(target_channel_id)
    print(f"Got channel {message_channel}")
    var = read_contents()
    if len(var)!=0:
        for i in range(0, len(var)):
            await message_channel.send(f'{var[i]} is airing today!')

@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()
    print("Finished waiting")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!schedule'):
        schedule = get_schedule()
        await message.channel.send(schedule)

    if message.content.startswith('!fav'):
        fav = message.content.split('!fav ')[1]
        with open("favs.txt", "a") as f:
            f.write(fav)
            f.write("\n")
        await message.channel.send('Favourite added!')

called_once_a_day.start()
client.run(os.environ.get('BOT_TOKEN'))
