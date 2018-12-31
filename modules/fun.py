import discord, json, asyncio, aiohttp, random
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as jsonresp:
            return await jsonresp.json()


class Fun_Commands:
    def __init__(self, bot):
        self.bot = bot
        self.ts_subcount = None
        self.pdp_subcount = None
        self.task = self.bot.loop.create_task(self.get_subcounts())

    def __unload(self):
        self.task.cancel()

    async def get_subcounts(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            pewdiepie = await get(f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UC-lHJZR3Gqxm24_Vd_AJ5Yw&key=" + self.bot.config['yt'])
            tes = await get(f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCq-Fj5jknLsUf-MWSy4_brA&key=" + self.bot.config['yt'])
            rawsubcount = int(pewdiepie['items'][0]['statistics']['subscriberCount'])
            tsrawcount = int(tes['items'][0]['statistics']['subscriberCount']) 
            self.ts_subcount = tsrawcount
            self.pdp_subcount = rawsubcount
            await asyncio.sleep(3600)

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, * , query):
        choices = self.bot.config['8ball']
        embed = discord.Embed(color=discord.Color(value=0xae2323), title=query, description="\uFEFF\n"+random.choice(choices))
        embed.set_author(name="8Ball Generator")
        embed.set_footer(text=self.bot.config['ver'], icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def subcount(self, ctx):
        pewdiepie = await get(f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UC-lHJZR3Gqxm24_Vd_AJ5Yw&key=" + self.bot.config['yt'])
        tes = await get(f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCq-Fj5jknLsUf-MWSy4_brA&key=" + self.bot.config['yt'])        
        rawsubcount = int(pewdiepie['items'][0]['statistics']['subscriberCount'])
        tsrawcount = int(tes['items'][0]['statistics']['subscriberCount'])

        rawdiff = (int(rawsubcount) - int(tsrawcount))
        subcount = f"**T-Series** needs **{rawdiff:,d}** subscribers to beat **PewDiePie**"

        if rawdiff <= 0:
            subcount = "T-Series has beaten PewDiePie :cry:"

        pdp = rawsubcount- self.pdp_subcount
        ts = tsrawcount - self.ts_subcount
        con = pdp - ts

        embed = discord.Embed(color=discord.Color(value=0xae2323))
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="PewDiePie", value=f"Currently has **{rawsubcount:,d}** subs, he has gained over **{pdp:,d}** subscribers per hour", inline=False)
        embed.add_field(name="T-Series", value=f"Currently has **{tsrawcount:,d}** subs, they have gained over **{ts:,d}** subscribers per hour", inline=False)
        embed.add_field(name="Sub Difference", value=f"{subcount}, and he has gained over **{con:,d}** more subscribers then T-Series within an hour", inline=False)
        embed.set_footer(text="PewDiePie's Subcount Tracker™ | " + self.bot.config['ver'], icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def poll(self, ctx, *, message):
        embed = discord.Embed(description=message, color=discord.Color(value=0xae2323))
        embed.set_author(name=f"New Poll from {ctx.author}", icon_url=ctx.author.avatar_url)
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
            await ctx.send("Error!, i can't add reactions to the embed")


    async def activitytype(self, status_type):
        if str(status_type) == "ActivityType.playing":
            return "Playing"
        elif str(status_type) == "ActivityType.streaming":
            return "Streaming"
        elif str(status_type) == "ActivityType.listening":
            return "Listening To"
        elif str(status_type) == 'ActivityType.watching':
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
        
        elif user == self.bot.user:
            username = f"{user} (PewDiePie Bot)"
            
        elif user.bot:
            username = f"{user} (Bot)"
        
        else:
            username = user
        if ctx.guild and len(user.roles) > 1:
            roles = '\n'.join(list(reversed(sorted([a.name for a in user.roles if a.name != "@everyone"]))))
        else:
            roles = "None"

        try:
            if str(user.status) == 'offline':
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
        embed.set_footer(text=f"User ID: {user.id} | " + self.bot.config['ver'], icon_url=self.bot.user.avatar_url)
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
        embed.set_footer(text=f"Server ID: {server.id} | "+ self.bot.config['ver'], icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


    @commands.command()
    async def meme(self, ctx):
        img = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4"]
        subreddits = ['dankmemes', "deepfriedmemes", "MemeEconomy", "PewDiePieSubmissions", "DonaldTrumpPepe", "DonaldTrumpMemes"]

        async def GetJSON(r):
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.reddit.com/r/{0}/hot.json?limit=300".format(r)) as resp:
                    return await resp.json()
    
  
        async def SearchURL():
            while True:
                urls = await GetJSON(random.choice(subreddits))
                number_of_indexing = 100
                passed = False
                while not passed:
                    try:
                        url = urls['data']['children'][random.randint(0, number_of_indexing)]['data']['url']
                        passed = True
                    except IndexError:
                        number_of_indexing-=1
                    except ValueError:
                        return await SearchURL()

                if url is not None:
                    for i in img:
                        if url.endswith(i):
                            return await ctx.send(url)
                        else:
                            continue
                            
        await SearchURL()        
            
            
        
                


def setup(bot):
    bot.add_cog(Fun_Commands(bot))
