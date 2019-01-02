import discord, asyncio, math, datetime, platform, pkg_resources, aiohttp
from discord.ext import commands

class Handler:
    def __init__(self, bot):
        self.bot = bot 

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            seconds = int(error.retry_after)
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            if ctx.command.name == "timely":
                return await ctx.send(embed=discord.Embed(color=discord.Color(value=0xae2323), title="Already recieved!", description=f"You already claimed your timely reward, try again in **{hours}**hrs, **{minutes}**m, **{seconds}**s"))
            else:
                return await ctx.send(embed=discord.Embed(description=f"You have reached the limit for the {ctx.command.name} command, please try again in **{hours}** hours and **{minutes}** minutes!", color=discord.Color.red()))
        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send(f"**This command cannot be used in a DM, please try this in a server**")
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f"I am missing `{error.missing_perms[0].replace('_', ' ')}` permission(s) to run this command")
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f"You are missing `{error.missing_perms[0].replace('_', ' ')}` permission(s) to run this command")
        elif isinstance(error, commands.CheckFailure):
            try:
                return await ctx.send(f"You do not have permissions to use the `{ctx.command}` command")
            except:
                pass
        elif isinstance(error, commands.MissingRequiredArgument):
            try:
                await ctx.command.reset_cooldown(ctx)
            except:
                pass
            return await ctx.send(f"You are missing an required argument: `{error.param.name}`")
        else:
            embed = discord.Embed(title=f"There is an error -> {ctx.command.name}", color=discord.Color.red())
            embed.add_field(name="Type", value=str(error.__class__.__name__), inline=False)
            embed.add_field(name="Traceback", value=error, inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            return await self.bot.get_channel(523715757398556702).send(embed=embed)
            
        
    async def on_command_completion(self, ctx):
        if ctx.cog.__class__.__name__ != "Developer_Tools":
            try:
                print(f"{ctx.author} used {ctx.command} at {ctx.channel.id} | {ctx.guild.name}")
            except:
                print(f"{ctx.author} used {ctx.command} at {ctx.channel.id}")
        else:
            pass
        await self.bot.db.execute("UPDATE commands SET num = commands.num + 1")
        
    async def on_ready(self):
        print(f"{self.bot.user} is ready")
        print("Python Version: " + str(platform.python_version()))
        print("Discord.py Version: " + str(pkg_resources.get_distribution('discord.py').version))
        print("Stats:\n")
        print("Guild Count: " + str(len(self.bot.guilds)))
        print("Members Count: " + str(len(set(self.bot.get_all_members()))))
        print("Total Channels: " + str(len(set(self.bot.get_all_channels()))))
        roles = await self.bot.db.fetch("SELECT * FROM shop")
        for i in roles:
            for b in self.bot.guilds:  
                for c in b.roles:
                    role = b.get_role(c.id)
                    if role is None:
                       print(f"Deleting Invalid Role: {role} ({c.id})")
                       await self.bot.db.execute("DELETE FROM shop WHERE guild_id=$1 AND role_id=$2", c.id, b.id)
                    else:
                        continue
                    
        await self.handler()
        data = await self.bot.db.fetch("SELECT * FROM bank")
        for i in data:
            if self.bot.get_guild(i['guild_id']) is None:
                await self.bot.db.execute("delete from bank where guild_id=$1", i['guild_id'])
                print(f"Deleted Guild Bank: ({i['guild_id']})")
            else:
                continue

    # Helper for the shop
    async def on_guild_role_delete(self, role):
        role_id = await self.bot.db.fetch("SELECT * FROM shop WHERE guild_id=$1", role.guild.id)
        for i in role_id:
            if i['role_id'] == role.id:
                await self.bot.db.execute("DELETE FROM shop WHERE role_id=$1 AND guild_id=$2", role.id, role.guild.id)
            else:
                continue
  
    async def on_guild_remove(self, guild):
        await self.handler()
        try:
            await self.bot.db.execute("DELETE FROM shop WHERE guild_id=$1", guild.id)
            await self.bot.db.execute("DELETE FROM bank WHERE guild_id=$1", guild.id)
        except:
            pass
        embed = discord.Embed(title="Lefted Guild", color=discord.Color(value=0xae2323))
        embed.add_field(name="Server", value=f"{guild} {guild.id}", inline=False)
        embed.add_field(name="Member Count", value=f"Currently {len(guild.members)} members", inline=False)
        embed.add_field(name="Owner", value=f"{guild.owner} | {guild.owner.id}", inline=False)
        embed.set_thumbnail(url=guild.icon_url)
        embed.timestamp = datetime.datetime.utcnow()
        await self.bot.get_channel(523715757398556702).send(embed=embed)

    async def on_guild_join(self, guild):
        await self.handler()
        embed = discord.Embed(title="Joined Guild", color=discord.Color(value=0xae2323))
        embed.add_field(name="Server", value=f"{guild} {guild.id}", inline=False)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Member Count", value=f"Currently {len(guild.members)} members", inline=False)
        embed.add_field(name="Owner", value=f"{guild.owner} | {guild.owner.id}", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await self.bot.get_channel(523715757398556702).send(embed=embed)
      
    async def handler(self):
        await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name=f"p.help | {len(self.bot.guilds)} servers!", url="https://twitch.tv/PewDiePie"))
        if self.bot.config["debug"] is False:
            async with aiohttp.ClientSession() as session:
               await session.post("https://discordbots.org/api/bots/" + str(self.bot.user.id) + "/stats", headers={'Authorization': self.bot.config['tokens']['dbltoken']},data={'server_count': len(self.bot.guilds)})
               await session.post("https://discordbots.group/api/bot/" + str(self.bot.user.id), headers={'Authorization' : self.bot.config['tokens']['dbgtoken']}, data={'server_count': len(self.bot.guilds)})



def setup(bot):
    bot.add_cog(Handler(bot))
