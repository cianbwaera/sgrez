
import discord
import json
import aiohttp
import asyncio
import datetime
import asyncpg
import pkg_resources
import time
import platform
from discord.ext import commands

class PewDiePie(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=self.prefix, case_insensitive=True)
       
    @property
    def config(self):
        return json.load(open("db/config.json"))

    def __str__(self):
        return self.config

    async def prefix(self, bot, message):
        prefix = await self.db.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", message.guild.id)
        if prefix is None:
            prefix = 'p.'
        return commands.when_mentioned_or(prefix)(bot, message)

    async def start(self, token, bot=True, reconnect=True):
        await self.login(token, bot=bot)
        try:
            await self.connect(reconnect=reconnect)
        except KeyboardInterrupt:
            await self.logout()


    async def on_connect(self):
        await self.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Connecting to Database.."))
        print("|====> Connecting to the database")
        creds = self.config['db-creds']
        try:
            self.db = await asyncpg.create_pool(**creds)
            print("Connected!")
            await self.db.execute(open('schema.sql').read())
        except asyncio.TimeoutError:
            print("Could not connect to the database:\nInvalid Host Address")
        except asyncpg.InvalidPasswordError:
            print("Invalid Password")
        except Exception as e:
            print(e)
            
    def run(self):
        self.uptime = datetime.datetime.utcnow()
        self.remove_command('help')
        self.load_extension("jishaku")
        cogs = self.config['cogs']
        for a in cogs:
            self.load_extension(a)
            print(f"<====|= Loaded Extension {a}") 
        print("|====> Posted Uptime")
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.start(self.config['tokens']['bottoken']))
        except KeyboardInterrupt:
            loop.run_until_complete(self.logout())
        
    async def logout(self):
        print("\nLogging out!\n")
        try:
            await self.db.close()
            print(f"\n\n|====>\/ Database closed \/<====|")
        except:
            pass
        await super().logout()
        

if __name__ == '__main__':
    PewDiePie().run()
