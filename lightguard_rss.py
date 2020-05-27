# destiny assistant bot for my destiny server
# this one chekcs rss feeds and is meant to run like once every 15 min
# author Nicky (@starmaid#6925)
# created 05/07/2020
# edited 05/26/2020
# version 1.2
# escaped &gt; and &lt;

import feedparser
import requests
import discord
import json

# look at previous updates
updates_path = './feed_updates.json'
try:
    with open(updates_path, 'r') as fp:
        last_update = json.load(fp)
except:
    last_update = {"twab": "None", "xur": "None"}

# twab updates
twab_update = False
twab = feedparser.parse('https://www.bungie.net/en/Rss/NewsByCategory?itemsPerPage=4&FILENAME=NewsRss&LOCALE=en')
title = twab['entries'][0]['title']
link = twab['entries'][0]['link']
if last_update['twab'] != title:
    twab_update = True
    last_update['twab'] = title


# xur updates
xur_update = False
xur = requests.get('https://wherethefuckisxur.com/')
#xur = requests.get('https://xurloc.tk/') rip to the fallen soldiers
#status = xur.text.split('<h1>')[1].split('</h1>')[0]
lines = xur.text.split('\n')
for l in lines:
    if "page-title" in l:
        xloc = l
        break

z = xloc.split('<')[1].split('>')[1]
status = z.replace('&#x27;','\'')
status = status.replace('&gt;','>')
status = status.replace('&lt;','<')

if last_update['xur'] != status:
    xur_update = True
    last_update['xur'] = status

# send the messages maybe
if twab_update or xur_update:
    with open(updates_path, 'w') as fp:
        json.dump(last_update, fp)

    client = discord.Client(activity=discord.Game("searching"))

    @client.event
    async def on_ready():
        for c in client.guilds[1].channels:
            if c.name == 'twab':
                twab_chan = c
            if c.name == 'bot-shit':
                bot_chan = c
        if twab_update:
            #send a twab update to the twab channel
            await twab_chan.send('`UPDATE FROM HEADQUARTERS ' + last_update['twab'] + '` ' + link)
        if xur_update:
            #send a xur update to the bot shit channel
            await bot_chan.send('`XUR LOCATION UPDATE: ' + last_update['xur'] + '`')
        await client.close()

    def read_token():
        token = None
        try:
            with open('./token.txt','r') as fp:
                token = fp.readlines()[0].strip('\n')
        except:
            print('Token file not found')
        return token

    token = read_token()
    if token is not None:
        client.run(token)
    else:
        pass
