import discord
import asyncio
import json
from discord.ext import commands

with open("./db/config.json", 'r') as file:
    config = json.load(file)

class Moderation:
    def __init__(self, bot):
        self.bot = bot


    # Yes I have made moderation commands but they were a pain in the ass to manage and i decided to just have a fun bot

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def clear(self, ctx, limit : int):
        msg = "message"
        if limit >= 600:
            limit = 600
        if limit > 1 or limit == 0:
            msg+='s'
        amt = await ctx.channel.purge(limit=limit + 1)
        await ctx.send(f"**I have cleared `{len(amt) - 1}` {msg} {config['tickyes']}**", delete_after=3.0)

def setup(bot):
    bot.add_cog(Moderation(bot))

    