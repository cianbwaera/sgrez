
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

with open("./db/config.json") as f:
    config = json.load(f)

cogs = config['cogs']

class PewDiePie(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=self.prefixes, case_insensitive=True, fetch_offline_members=False)
        self.db = None

    def prefixes(self, bot, message):
        default_prefixes = ['p.', 'P.', 'pewdiepie.']
        return commands.when_mentioned_or(*default_prefixes)(bot, message)

    async def on_ready(self):
        print(f"{self.user} is ready")
        print("Python Version: " + str(platform.python_version()))
        print("Discord.py Version: " + str(pkg_resources.get_distribution('discord.py').version))
        print("Stats:\n")
        print("Guild Count: " + str(len(self.guilds)))
        print("Members Count: " + str(len(set(self.get_all_members()))))
        print("Total Channels: " + str(len(set(self.get_all_channels()))))
        print('\uFEFF')
        await self.handler()


    async def on_guild_remove(self, guild):
        await self.handler()
        embed = discord.Embed(title="Lefted Guild", color=discord.Color(value=0xae2323))
        embed.add_field(name="Server", value=f"{guild} {guild.id}", inline=False)
        embed.add_field(name="Member Count", value=f"Currently {len(guild.members)} members", inline=False)
        embed.add_field(name="Owner", value=f"{guild.owner} | {guild.owner.id}", inline=False)
        embed.set_thumbnail(url=guild.icon_url)
        embed.timestamp = datetime.datetime.utcnow()
        await self.get_channel(523715757398556702).send(embed=embed)

    async def on_guild_join(self, guild):
        await self.handler()
        embed = discord.Embed(title="Joined Guild", color=discord.Color(value=0xae2323))
        embed.add_field(name="Server", value=f"{guild} {guild.id}", inline=False)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Member Count", value=f"Currently {len(guild.members)} members", inline=False)
        embed.add_field(name="Owner", value=f"{guild.owner} | {guild.owner.id}", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.get_channel(523715757398556702).send(embed=embed)
        try:
            embed = discord.Embed(color=discord.Color(value=0xae2323))
            embed.set_author(name=f"Thanks for inviting PewDiePie!")
            embed.set_thumbnail(url=self.user.avatar_url)
            embed.add_field(name="Getting Started", value=f"Send`p.help` for a list of my commands and if you ever need any support, [click here]({config['server']})")
            embed.add_field(name="Helping ", value="Although this isnt required, it would be appreciated of you upvote me at the following links\n[Discord Bot List](https://discordbots.org/bot/508143906811019269/vote)\n[Discord Bots Group](https://discordbots.group/bot/508143906811019269)")
            embed.set_footer(text=f"I use to have {len(self.guilds-1)} servers, but thanks to you, i now have {len(self.guilds)} servers!")
            await guild.system_channel.send(embed=embed)
        except:
            pass

    async def handler(self):
        await self.change_presence(activity=discord.Streaming(name=f"p.help in {len(self.guilds)} servers!", url="https://twitch.tv/PewDiePie"))
        if config["debug"] is False:
            async with aiohttp.ClientSession() as session:
               await session.post("https://discordbots.org/api/bots/508143906811019269/stats", headers={'Authorization': config['tokens']['dbltoken']},data={'server_count': len(self.guilds)})
               await session.post("https://discordbots.group/api/bot/508143906811019269/", headers={'Authorization' : config['tokens']['dbgtoken']}, data={'server_count': len(self.guilds)})

    async def start(self, token, bot=True, reconnect=True):
        await self.login(token, bot=bot)
        try:
            await self.connect(reconnect=reconnect)
        except KeyboardInterrupt:
            await self.logout()


    async def on_connect(self):
        await self.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Connecting to DB.."))
        print("|====> Connecting to the database")
        creds = config['db-creds']
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
        for a in cogs:
            self.load_extension(f'modules.{a}')
            print(f"<====| Loaded Extension modules.{a}") 
        print("|====> Posted Uptime")
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.start(config['tokens']['bottoken']))
        except KeyboardInterrupt:
            loop.run_until_complete(self.logout())
        
    async def logout(self):
        print("\nLogging out!\n")
        try:
            time1 = time.perf_counter()
            await self.db.close()
            time2 = time.perf_counter()
            res = round((time2-time1)*1000)
            print(f"\n\n|====> Database closed in {res}ms <====|")
        except Exception as e:
            print(e)
        await super().logout()
        

if __name__ == '__main__':
    PewDiePie().run()
