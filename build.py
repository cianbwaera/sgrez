
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
        super().__init__(command_prefix=self.prefixes, case_insensitive=True)

    
    @property
    def config(self):
        return json.load(open("db/config.json"))

    def __str__(self):
        return self.self.bot.config

    def prefixes(self, bot, message):
        default_prefixes = ['p.', 'P.', 'pewdiepie.']
        return commands.when_mentioned_or(*default_prefixes)(bot, message)


    async def start(self, token, bot=True, reconnect=True):
        await self.login(token, bot=bot)
        try:
            await self.connect(reconnect=reconnect)
        except KeyboardInterrupt:
            await self.logout()


    async def on_connect(self):
        await self.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Connecting to DB.."))
        print("|====> Connecting to the database")
        creds = self.config['db-creds']
        try:
            self.db = await asyncpg.create_pool(**creds)
            print("Connected!")
            await self.db.execute(open('schema.sql').read())
        except asyncio.TimeoutError:
            await self.change_presence(status=discord.Status.dnd, activity=discord.Game(name="DB Connection failed!"))
            print("Could not connect to the database:\nInvalid Host Address")
        except asyncpg.InvalidPasswordError:
            await self.change_presence(status=discord.Status.dnd, activity=discord.Game(name="DB Connection failed!"))
            print("Invalid Password")
        except Exception as e:
            await self.change_presence(status=discord.Status.dnd, activity=discord.Game(name="DB Connection failed!"))
            print(e)
            
    def run(self):
        json.dump({"uptimestats" : str(datetime.datetime.utcnow())}, open("db/uptime.json", "w+"))
        self.remove_command('help')
        self.load_extension("jishaku")
        cogs = self.config['cogs']
        for a in cogs:
            self.load_extension(f'modules.{a}')
            print(f"<====|= Loaded Extension modules.{a}") 
        print("|====> Posted Uptime")
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.start(self.config['tokens']['bottoken']))
        except KeyboardInterrupt:
            loop.run_until_complete(self.logout())
        
    async def logout(self):
        print("\nLogging out!\n")
        try:
            time1 = time.perf_counter()
            await self.db.close()
            time2 = time.perf_counter()
            res = round((time2-time1)*1000)
            print(f"\n\n|====>\/Database closed in {res}ms\/<====|")
        except:
            pass
        await super().logout()
        

if __name__ == '__main__':
    PewDiePie().run()
