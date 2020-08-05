# destiny assistant bot for my destiny server
# author Nicky (@starmaid#6925)
# created 05/06/2020
# edited 05/07/2020
# version 1.0

import discord
from datetime import datetime, timezone, timedelta
from dateutil import parser
import asyncio
from discord.ext import commands
import random
from random import choice

class Devent:
    def __init__(self,name,string):
        try:
            self.time = parser.parse(string,fuzzy=True)
        except Exception as err:
            raise err
        self.name = name
        self.notified = False
        return

    def until(self):
        self.delta = self.time - datetime.today()
        return self.delta

    def __str__(self):
        return self.name + ' ' + str(self.time) + ' ' + str(self.until())


class Bot(commands.Bot):
    phrases = [
        'lightguard'
    ]
    replies = [
        '`yes, crew member?`'
    ]
    activity = 'subroutines'
    logoff_msg = '`shutting down`'

    events = []
    updates_chan = None

    def __init__(self):
        # This is the stuff that gets run at startup
        super().__init__(command_prefix='>',self_bot=False,activity=discord.Game(self.activity))
        self.remove_command('help')
        self.add_command(self.help)
        self.add_command(self.event)
        self.add_command(self.quit)
        self.read_token()

        if self.token is not None:
            super().run(self.token)
        else:
            pass

    def read_token(self):
        self.token = None
        try:
            with open('./token.txt','r') as fp:
                self.token = fp.readlines()[0].strip('\n')
        except:
            print('Token file not found')

    async def on_ready(self):
        for c in self.guilds[1].channels:
            if c.name == 'bot-shit':
                self.updates_chan = c
        asyncio.run_coroutine_threadsafe(self.clock(),self.loop)
        print('Logged on')

    async def clock(self):
        # check time until events
        while True:
            self.events.sort(reverse=True,key=lambda x: x.until())
            for e in self.events:
                timeuntil = e.until().total_seconds()
                if timeuntil / 60 < 15 and e.notified == False:
                    await self.updates_chan.send(await self.clock_msg(e))
                    await self.change_presence(activity=discord.Game(e.name))
                    e.notified = True
                if timeuntil < 0:
                    self.events.remove(e)
                    await self.change_presence(activity=discord.Game(self.activity))
            # wait 10 minutes
            #print('sleeping')
            await asyncio.sleep(60*1)

    async def clock_msg(self,e):
        # adds formatting to the message that an event is occuring
        return '`event ' + e.name + ' is occuring in ' + str(e.until()/timedelta(minutes=1)) + ' minutes`'

    def gen_reply(self, words, type):
        msg = 'u said'
        for w in words:
            msg = msg + ' `'  + w + '`'
            if w != words[len(words) - 1]:
                msg = msg + ', '
        msg = msg + ' - '
        if type == 1:
            msg = msg + choice(self.hs_replies)
        elif type == 2:
            msg = msg + choice(self.suspicious)
        return msg

    @commands.command(pass_context=True)
    async def help(ctx):
        #this is the help command.
        help_msg = '```<+> lightguard <+>\n' + \
            'a discord bot to help guardians perform their duties ' + \
            'to protect the city and the traveler' + \
            '\nusage:          >command [params]*' + \
            '\n --- availible commands ---' + \
            '\n>help                                    shows this message' + \
            '\n>event add [event_name] [date and time]  adds event (EST)' + \
            '\n>event list                              lists current events' + \
            '\n>event del [name]                        deletes event [name]' + \
            '\n>quit                                    shuts down the bot (only works for starmaid)' + \
            '```'
        await ctx.send(help_msg)
        return

    @commands.command(pass_context=True)
    async def event(ctx):
        #manage events in the server.
        message = ctx.message.content.lower()
        msg = message.split()
        print(msg)
        #add
        #del
        #list

        l = len(msg)
        if l < 2:
            await ctx.send('`please add a parameter`')
            return

        cmd = msg[1]
        reply = ''

        if cmd == 'add':
            if l < 4:
                reply = '`incorrect number of params for ' + cmd + ' (' + str(l) + ')`'
            else:
                try:
                    date = ''
                    for i in range(3,l):
                        date += msg[i] + ' '
                    ev = Devent(msg[2],date)
                    ctx.bot.events.append(ev)
                    reply = '`event added sucessfully`'
                except Exception as ex:
                    reply = '`invalid timestring`'
        elif cmd == 'del':
            if l != 3:
                reply = '`incorrect number of params for ' + cmd + ' (' + str(l) + ')`'
            else:
                if len(ctx.bot.events) == 0:
                    reply = '`no events planned`'
                else:
                    fail = 1
                    for ev in ctx.bot.events:
                        if ev.name == msg[2]:
                            ctx.bot.events.remove(ev)
                            reply = '`deleted sucessfully`'
                            fail = 0
                            break
                    if fail == 1:
                        reply = '`unable to delete`'
        elif cmd == 'list':
            if len(ctx.bot.events) == 0:
                reply = '`no events planned`'
            else:
                out = '`'
                for ev in ctx.bot.events:
                    out += str(ev) + '\n'
                out += '`'
                reply = out
        else:
            reply = '`unknown command parameter`'
        await ctx.send(reply)
        return

    @commands.command(pass_context=True)
    async def quit(ctx):
        # quits the bot.
        if str(ctx.message.author) == 'starmaid#6925':
            await ctx.send(ctx.bot.logoff_msg)
            await ctx.bot.close()
        else:
            await ctx.send('`you do not have permission to shut me down.`')
        return


if __name__ == '__main__':
    Bot()
