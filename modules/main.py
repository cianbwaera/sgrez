import discord, asyncio, aiohttp, time, random, datetime, json, psutil, platform, pkg_resources
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from time import ctime

with open('db/config.json') as file:
    config = json.load(file)

def_color = 0xae2323

class Main_Commands:
    def __init__(self, bot):
        self.bot = bot
  
    @commands.command(aliases=['server'])
    async def support(self, ctx):
        try:
            await ctx.author.send(f"**Here's My Support Server**\n{self.bot.config['server']}")
            await ctx.send("**Check DMs for Support Server :mailbox_with_mail:**")
        except:
            await ctx.send(f"**Here's My Support Server**\n{self.bot.config['server']}")

    @commands.command()
    async def perms(self, ctx, user: discord.Member=None):
        if not user:
            user = ctx.author
        perms = '\n'.join(permission for permission,val in user.guild_permissions if val).replace('_', ' ')
        embed = discord.Embed(color=discord.Color(value=def_color))
        embed.set_author(name=f"Permissions For {user}", icon_url=user.avatar_url)
        embed.add_field(name='\uFEFF', value=perms)
        embed.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild)
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        await ctx.send(f"**Here's My Help Page**\n<https://enternewname.me/pewdiepie>")

    @commands.command()
    async def prefix(self, ctx):
        if self.bot.user.mentioned_in(ctx.message):
            await ctx.send("My prefix is `p.` or you can mention me for commands")

    @commands.command()
    async def uptime(self, ctx):
        time = json.load(open('db/uptime.json', "r"))['uptimestats']
        uptimeraw = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
        uptime = datetime.datetime.utcnow() - uptimeraw
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"I've been running for **{days}** days, **{hours}** hours, **{minutes}** minutes, **{seconds}** seconds")

    @commands.cooldown(1, 10, BucketType.channel)
    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(title=f"{self.bot.user.name}'s Ping", color=discord.Color(value=def_color), description="Calculated the latency and ping of PewDiePie")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        msg = await ctx.send(f"`Pinging 0/3`")
        avg = []
        counter = 0
        for _ in range(3):
            counter+=1 
            t1 = time.perf_counter()
            await msg.edit(content=f"`Pinging {counter}/3`")
            t2 = time.perf_counter()
            ping = round((t2-t1)*1000)
            avg.append(ping)
            embed.add_field(name=f"Ping {counter}", value=f"{ping}ms", inline=False)
        embed.add_field(name="Bot latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.add_field(name="Average Speed", value=f"{round((sum(avg)) / len(avg))}ms", inline=False)
        embed.set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.avatar_url)
        await msg.edit(content=None, embed=embed)
            
    @commands.command()
    async def invite(self, ctx):
        try:
            perms = discord.Permissions(8)
            await ctx.author.send(f"**Here's My Invite Link**\n**{discord.utils.oauth_url(self.bot.user.id, perms)}**")
            await ctx.send("**Check DM's For Bot Invite :mailbox_with_mail:**")
        except:
            await ctx.send(f"**Here's My Invite Link**\n**{discord.utils.oauth_url(self.bot.user.id, perms)}**")

    async def get(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as jsonresp:
                return await jsonresp.json()

    @commands.command()
    async def stats(self, ctx):
        timess = json.load(open('db/uptime.json', "r"))['uptimestats']

        uptimeraw = datetime.datetime.strptime(timess, "%Y-%m-%d %H:%M:%S.%f")

        uptime = datetime.datetime.utcnow() - uptimeraw
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        commands_used = await self.bot.db.fetchval("SELECT num FROM commands")
      
        latency = str(round(self.bot.latency * 1000))
        gh_branch = "master"
        gh = await self.get("https://api.github.com/repos/EnterNewName/PewDiePie/commits/" + gh_branch)
        sha = gh['sha']
        commit = sha[0:7]        
        message = gh['commit']['message']
        embed = discord.Embed(color=discord.Color.blurple(), title=f"{self.bot.user}", description=f"A discord bot made from Enter New Name orginally made for showing the subcount of PewDiePie and T-Series\n\uFEFF")
        embed.add_field(name="Commands Used", value=f"I have a total of {commands_used:,d} commands used")
        embed.add_field(name="Uptime", value=f"I have been running for **{days}** days, **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds!")
        embed.add_field(name="Support the Development", value="[Donate to us on Patreon](https://patreon.com/pewdiepiebot)\n[Discord Bot List](https://discordbots.org/bot/508143906811019269/vote)\n[Discord Bots Group](https://discordbots.group/bot/508143906811019269)\uFEFF\n", inline=False)
        embed.add_field(name="Recent GitHub Update", value=f"```fix\n[PewDiePie:{gh_branch}] | [{commit}]:\n{gh['commit']['author']['name']} - {message}\n```")
        dev_update = await self.bot.db.fetchval("SELECT updates FROM development")
        embed.add_field(name=f"Recent Developer Update", value=f"```md\n{dev_update}\n```")
        await ctx.send(embed=embed)



    @commands.command()
    async def systeminfo(self, ctx):
        
        # Get some information before sending embed to make it look better

        cpu_stats = f"{psutil.cpu_percent(interval=None)}%"
        vir_mem = f"{psutil.virtual_memory()[2]}%"

        all_cpus = psutil.cpu_count()

        non_log_cpus = psutil.cpu_count(logical=False)

        t1 = time.perf_counter()
        await self.bot.db.fetch("SELECT * FROM commands LIMIT 1")
        t2 = time.perf_counter()
        dbping = round((t2-t1)*1000)
        
        dpy_ver = str(pkg_resources.get_distribution('discord.py').version)
        tcu = await self.bot.db.fetchval("SELECT COUNT(*) FROM bank")


        # Make the embed

        embed = discord.Embed(color=discord.Color.blurple(), title="System Usage and Info", description="This is my runtime stats, how much speed i have, and how much data i process. If you want to help me run faster, donate to the [patreon](https://patreon.com/pewdiepiebot)")
        embed.add_field(name="RAM Usage :gear:", value=f"Memory Usage: {vir_mem}\n", inline=False)
        embed.add_field(name="CPU Stats", value=f"CPU Count: {all_cpus}\nCPU Count (non-logical): {non_log_cpus}", inline=False)
        embed.add_field(name="Database Information :bar_chart:", value=f"Database Provider: postgresql\nPing: {dbping}ms\nTotal Currency Users: {tcu:,d}", inline=False)
        embed.add_field(name="General Stats", value=f"<:python3:490607334876381204> Python Version: {platform.python_version()}\n<:discord:528452385023066112> Discord.py Version: {dpy_ver}", inline=False)
        await ctx.send(embed=embed)
       
        
def setup(bot):
    bot.add_cog(Main_Commands(bot))
