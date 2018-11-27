import discord, asyncio, aiohttp, time, random, datetime, json, psutil, platform, pkg_resources
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from time import ctime

with open('db/config.json') as file:
    config = json.load(file)

def_color = 0xae2323

class MainClass:
    def __init__(self, bot):
        self.bot = bot
     

    @commands.command(aliases=['server'])
    async def support(self, ctx):
        await ctx.send(embed=discord.Embed(color=discord.Color(value=def_color), title="Here's My Support Server", description=f"[Click Here]({config['server']})"))

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
        emb = discord.Embed(title="PewDiePie's Commands", description=f"A list of commands that everyone can use with the bot, if you have any trouble, you can join the [Support Server]({config['server']}) for more help!", color=discord.Color(value=def_color))
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.add_field(name="@PewDiePie#7718 prefix", value="The prefix is p., but it is here just in case!", inline=False)
        emb.add_field(name="p.invite", value="PewDiePie sends you his invite", inline=False)
        emb.add_field(name="p.support or p.server", value=f"PewDiePie sends you his super awesome [Support Server]({config['server']})", inline=False)
        emb.add_field(name="p.ping", value="You can get my speed of the discord websocket connection", inline=False)
        emb.add_field(name="p.stats", value="You can get my current statistics such as guild count, commands used, etc", inline=False)
        emb.add_field(name="p.uptime", value="You can get how long i have been running for", inline=False)
        emb.add_field(name="p.help", value="Shows you this message, you should know that though", inline=False)
        emb.add_field(name="p.clear (amount)", value="Purges messages specifically in that channel", inline=False)
        emb.add_field(name="p.userinfo", value="I send you the current information of you or an user", inline=False)
        emb.add_field(name="p.serverinfo", value="I send you the current information of your server", inline=False)
        emb.add_field(name="p.perms", value="You recieve the current permissions of you/an user in your server", inline=False)
        emb.add_field(name="p.subcount", value="This command gets the subcount of T-Series and PewDiePie", inline=False)
        emb.add_field(name="p.feedback (feedback)", value="You can send feedback to us, please do not abuse though")
        emb.add_field(name="p.poll (poll message)", value="Creates a poll to debate over!", inline=False)
        emb.add_field(name="p.8ball (question)", value="You can ask a question to the 8ball and it will respond", inline=False)
        emb.add_field(name="p.bal or p.$ or p.balance", value="How many pewdiecoins do you have", inline=False)
        emb.add_field(name="p.timely", value="Free 75 coins each hour", inline=False)
        emb.add_field(name="p.coinflip", value="Flips a coin, you either win that amount or lose that amount if you get it correct", inline=False)
        emb.add_field(name="p.leaderboard or p.lb", value="PewDieCoin Leaderboard", inline=False)
        emb.add_field(name="p.give", value="Exchange coins with other Users", inline=False)
        emb.add_field(name="p.shop", value="Shows the availible items (roles) are on the shop")
        emb.add_field(name="p.buy (item_id)", value="Buy a role off the shop", inline=False)
        emb.add_field(name="p.sell (amount) (role_name/id)", value="Add a role to the shop")
        emb.add_field(name="p.remove (item_id)", value="Remoes a role off the shop", inline=False)
        emb.set_footer(text="Economy (PewDieCoin) Commands Are in BETA | " + config['ver'])
        try:
            await ctx.author.send(embed=emb)
            await ctx.send("**Check you DMs For Help:mailbox_with_mail:**")
        except:
            await ctx.send(f"{ctx.author.mention}, please have open DMs so i can send you help!")

    @commands.command()
    async def prefix(self, ctx):
        if self.bot.user.mentioned_in(ctx.message):
            await ctx.send("My prefix is `p.` or mention me")

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
        perms = discord.Permissions.all()
        await ctx.send(embed=discord.Embed(color=discord.Color(value=def_color), title="Here's My Invite",description=f"[Click Here!]({discord.utils.oauth_url(self.bot.user.id, perms)})"))

    async def get(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as jsonresp:
                return await jsonresp.json()

    @commands.command()
    async def stats(self, ctx):
        time = json.load(open('db/uptime.json', "r"))['uptimestats']
        uptimeraw = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
        uptime = datetime.datetime.utcnow() - uptimeraw
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        cpu_stats = f"{psutil.cpu_percent()}%"
        vir_mem = f"{psutil.virtual_memory()[2]}%"
        commands_used = await self.bot.db.fetchval("SELECT num FROM commands")
        dpy_ver = str(pkg_resources.get_distribution('discord.py').version)
        python_ver = str(platform.python_version())
        latency = str(round(self.bot.latency * 1000))
        gh_branch = "master"
        gh = await self.get("https://api.github.com/repos/EnterNewName/PewDiePie/commits/" + gh_branch)
        sha = gh['sha']
        commit = sha[0:7]        
        message = gh['commit']['message']
        embed = discord.Embed(color=discord.Color(value=def_color), title=f"{self.bot.user}", description=f"A discord bot made from Enter New Name orginally made for showing the subcount of PewDiePie and T-Series")
        embed.add_field(name="Bot Info", value=f"I have been running for approx. **{days}** days, **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds\nI have {len(self.bot.guilds)} servers\n{commands_used} commands were used in my guilds", inline=False)
        embed.add_field(name="Versions:", value=f"PewDiePie's Version: {config['ver']}\nDiscord.py Version: {dpy_ver}\nPython Version: {python_ver}", inline=False)
        embed.add_field(name="System Info:", value=f"I am using {cpu_stats} of my CPU with a latency of {latency}ms and {vir_mem} of my memory has been used", inline=False)
        embed.add_field(name="Support Us", value="[Upvote Me on Discord Bot List](https://discordbots.org/bot/508143906811019269/vote)\n[Upvote Me on Discord Bots Group](https://discordbots.group/bot/508143906811019269)", inline=False)
        embed.add_field(name="Updates", value=f"```fix\n[PewDiePie:{gh_branch}] | [{commit}]:\n{gh['commit']['author']['name']} - {message}\n```")
        await ctx.send(embed=embed)


    @commands.guild_only()
    @commands.command()
    @commands.cooldown(1, 1800, BucketType.user)
    async def feedback(self, ctx, * , feedback : str):
        channel = self.bot.get_channel(517107620042244098)
        embed = discord.Embed(description=f"User ID: {ctx.author.id} | User Name: {ctx.author}", title="Feedback Submission :pencil:", color=discord.Color(value=0xae2323))
        embed.add_field(name="Feedback", value=feedback, inline=False)
        embed.set_footer(text=f"From {ctx.guild.name} ({ctx.guild.id})")
        await channel.send(embed=embed)
        await ctx.send(f"**Your Feedback Has Been Submitted {config['tickyes']}**")

def setup(bot):
    bot.add_cog(MainClass(bot))
