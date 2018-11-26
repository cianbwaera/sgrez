import discord, json, asyncio, aiohttp, random
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as jsonresp:
            return await jsonresp.json()


with open('db/config.json') as file:
    config = json.load(file)

class FunCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, * , query):
        choices = config['8ball']
        embed = discord.Embed(color=discord.Color(value=0xae2323))
        embed.add_field(name=query, value=random.choice(choices))
        embed.set_author(name="Eight Ball")
        embed.set_footer(text=config['ver'], icon_url=self.bot.user.avatar_url)
        try:
            ctx.message.delete()
        except:
            pass
        await ctx.send(embed=embed)

    @commands.cooldown(2, 15, BucketType.channel)
    @commands.command()
    async def subcount(self, ctx):
        pewdiepie = await get(f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UC-lHJZR3Gqxm24_Vd_AJ5Yw&key=" + config['yt'])
        tes = await get(f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCq-Fj5jknLsUf-MWSy4_brA&key=" + config['yt'])        
        rawsubcount = pewdiepie['items'][0]['statistics']['subscriberCount']
        tsrawcount = tes['items'][0]['statistics']['subscriberCount']
        subcount = rawsubcount[:2]+','+rawsubcount[2:5]+','+rawsubcount[5:]        
        tssubcount = tsrawcount[:2]+','+tsrawcount[2:5]+','+tsrawcount[5:]
        rawdiff = (int(rawsubcount) - int(tsrawcount))
        embed = discord.Embed(color=discord.Color(value=0xae2323))
        embed.set_author(name="Current Statistics")
        embed.add_field(name="PewDiePie Count", value=subcount, inline=False)
        embed.add_field(name="T-Series Count", value=tssubcount, inline=False)
        embed.add_field(name="Sub Difference", value=f"only {int(rawdiff)} subscribers to beat Pewd", inline=False)
        embed.add_field(name="Live Sub Counts", value="[PewDiePie Subcount](https://socialblade.com/youtube/user/pewdiepie/realtime), [T-Series Subcount](https://socialblade.com/youtube/user/tseries/realtime)")
        embed.set_footer(text="PewDiePie SubCount Tracker™ | " + config['ver'], icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def poll(self, ctx, *, poll_message):
        embed = discord.Embed(description=poll_message, color=discord.Color(value=0xae2323))
        embed.set_author(name=f"New poll from {ctx.author}", icon_url=ctx.author.avatar_url)
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send(embed=embed)        
        try:
            await msg.add_reaction("\N{THUMBS UP SIGN}")
            await msg.add_reaction("\N{THUMBS DOWN SIGN}")
        except:
            await msg.delete()
            await ctx.send("Make sure i can add reactions to the poll")


    async def activitytype(self, activitytype):
        if str(activitytype) == "ActivityType.playing":
            return "Playing"
        elif str(activitytype) == "ActivityType.streaming":
            return "Streaming"
        elif str(activitytype) == "ActivityType.listening":
            return "Listening To"
        elif str(activitytype) == 'ActivityType.watching':
            return "Watching"
        else:
            pass

    @commands.command()
    async def userinfo(self, ctx, * , user : discord.Member=None):
        if not user:
            user = ctx.author
        if ctx.guild:
            joined_server = user.joined_at.strftime("%B %e, %Y %I:%M%p")
            server_stay_length = (ctx.message.created_at - user.joined_at).days
        joined_discord = user.created_at.strftime("%B %e, %Y %I:%M%p")
        created_account_length = (ctx.message.created_at - user.created_at).days
        if user.id == self.bot.owner_id:
            username = f"{user} (My Owner)"
        elif user.bot:
            username = f"{user} (Bot)"
        else:
            username = user
        if ctx.guild and len(user.roles) > 1:
            roles = '\n'.join(list(reversed(sorted([a.name for a in user.roles if a.name != "@everyone"]))))
        else:
            roles = "None"

        try:
            if user.status.offline:
                activity = f"{user.name} is offline"
            else:
                authoracttype = await self.activitytype(user.activity.type)
                activity = f"{authoracttype} {user.activity.name}"
        except:
            activity = f"{user.name} isn't playing anything"

        embed = discord.Embed(description=activity, color=discord.Color(value=0xae2323))
        if ctx.guild and user.nick:
            embed.set_author(name=f"{username} ({user.nick})")
        else:
            embed.set_author(name=username)
        embed.set_thumbnail(url=user.avatar_url)
        if ctx.guild:
            embed.add_field(name="Joined Server", value=f"{joined_server}, {server_stay_length} Days ago", inline=False)
        embed.add_field(name="Joined Discord", value=f"{joined_discord}, {created_account_length} Days ago", inline=False)
        if ctx.guild:
            embed.add_field(name="Roles", value=roles)
        embed.set_footer(text=f"User ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def serverinfo(self, ctx):
        server = ctx.guild
        membercount = len(server.members)
        roles = list(reversed(sorted([a.name for a in server.roles if a.name != "@everyone"])))
        online_count = len([x.status for x in server.members if x.status == discord.Status.online or x.status == discord.Status.dnd or x.status == discord.Status.idle])
        bots = len([x.name for x in server.members if x.bot])
        humans = len([x.name for x in server.members if not x.bot])
        guild_created_days =  (ctx.message.created_at - server.created_at).days
        guild_created_time = server.created_at.strftime("%B %e, %Y %I:%M%p")
        embed = discord.Embed(title=str(server), color=discord.Color(value=0xae2323), description=f"Created over {guild_created_days} days ago at {guild_created_time} from {server.owner}")
        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="Bot Count", value=f"{bots}/{membercount}", inline=False)
        embed.add_field(name="Human Count", value=f"{humans}/{membercount}", inline=False)
        embed.add_field(name="Member Count", value=membercount, inline=False)
        embed.add_field(name="Online", value=f"{online_count}/{membercount}", inline=False)
        embed.add_field(name="Server Region", value=server.region, inline=False)
        embed.add_field(name="Roles", value=len(roles), inline=False)
        embed.set_footer(text=f"Server ID: {server.id}")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(FunCommands(bot))
