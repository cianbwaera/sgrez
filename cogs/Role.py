import discord, json, asyncio, datetime
from discord.ext import commands

with open("db/config.json", "r") as f:
    config = json.load(f)

class Role:
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def giverole(self, ctx, user : discord.Member, *, role : discord.Role):
        if ctx.author.top_role > user.top_role or ctx.author == ctx.guild.owner:
            await user.add_roles(role)
            await ctx.send(f"***{config['tickyes']} Gave {user.mention} Role: `{role}`***")
            try:
                embed = discord.Embed(timestamp=datetime.datetime.utcnow(), color=discord.Color(value=0xae2323))
                embed.set_author(name=f"Moderator Action: {ctx.command}")
                embed.add_field(name="Moderator:", value=ctx.author, inline=False)
                embed.add_field(name="Role Recieved:", value=role, inline=False)
                embed.add_field(name="Acclaimed User", value=user, inline=False)
                embed.set_footer(text=f"Moderator ID: {ctx.author.id}")
                modlog = discord.utils.get(ctx.guild.text_channels, name="mod-log")
                await modlog.send(embed=embed)
            except: 
                pass

    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def removerole(self, ctx, user : discord.Member, *, role : discord.Role):
        if ctx.author.top_role >= user.top_role or ctx.author == ctx.guild.owner:
            await user.remove_roles(role)
            await ctx.send(f"***{config['tickyes']} Ok, {user.mention} has been removed from role: `{role}`***")
            try:
                embed = discord.Embed(timestamp=datetime.datetime.utcnow(), color=discord.Color(value=0xae2323))
                embed.set_author(name=f"Moderator Action: {ctx.command}")
                embed.add_field(name="Moderator:", value=ctx.author, inline=False)
                embed.add_field(name="Role Removed:", value=role, inline=False)
                embed.add_field(name="Acclaimed User", value=user, inline=False)
                embed.set_footer(text=f"Moderator ID: {ctx.author.id}")
                modlog = discord.utils.get(ctx.guild.text_channels, name="mod-log")
                await modlog.send(embed=embed)
            except:
                pass
        
def setup(bot):
    bot.add_cog(Role(bot))