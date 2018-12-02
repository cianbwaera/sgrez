import discord, asyncio, math, datetime
from discord.ext import commands

class Error_Handler:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            if ctx.command.name == 'timely':
                return await ctx.send(embed=discord.Embed(color=discord.Color(value=0xae2323), description=f'You already got your timely reward, try again in **{hours}**h, **{minutes}**m, and **{seconds}**s'))
            else:
                return await ctx.send(f"You can run the {ctx.command} command again in **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds") 
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
        else:
            print(error)
        
    async def on_command_completion(self, ctx):
        if ctx.cog.__class__.__name__ != "OwnerCommands":
            print(f"{ctx.author} used {ctx.command} at {ctx.channel.id}")
        else:
            pass
        await self.bot.db.execute("UPDATE commands SET num = num + 1")
        


    # Helper for the shop
    async def on_guild_role_delete(self, role):
        role_id = await self.bot.db.fetch("SELECT * FROM shop WHERE guild_id=$1", role.guild.id)
        for i in role_id:
            if i['role_id'] == role.id:
                await self.bot.db.execute("DELETE FROM shop WHERE role_id=$1 AND guild_id=$2", role.id, role.guild.id)
            else:
                continue


def setup(bot):
    bot.add_cog(Error_Handler(bot))
