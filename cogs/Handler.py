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
            if ctx.command.name == 'daily':
                return await ctx.send(embed=discord.Embed(color=discord.Color(value=0xae2323), description=f'You already got your timely reward, try again in **{hours}**h, **{minutes}**m, and **{seconds}**s'))
            else:
                return await ctx.send(f"You can run the {ctx.command} command again in **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds")                
        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send(f"**This command cannot be used in a DM, please try this in a server**")
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f"I am missing `{error.missing_perms[0].replace('_', ' ')}` permission(s) to run this command")
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f"You are missing `{error.missing_perms[0].replace('_', ' ')}` permission(s) to run this command")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"`{error.param}` is a required argument")
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(f"You do not have permissions to use the `{ctx.command}` command")
        else:
            print(error)
        
    async def on_command(self, ctx):
        if ctx.cog.__class__.__name__ != "OwnerCommands":
            print(f"{ctx.author} used {ctx.command} at {ctx.channel.id}")
        else:
            pass

    async def on_command_completion(self, ctx):
        await self.bot.db.execute("UPDATE pdp_cmds SET cmdcount = cmdcount + 1")


def setup(bot):
    bot.add_cog(Error_Handler(bot))
