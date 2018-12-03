import discord
import asyncio
from discord.ext import commands

ffmpeg_options = {
    'option' : "-vn"
}

class Music:
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group()
    async def disstrack(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid Arguments")

    @disstrack.command()
    async def play(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are currently not connected to a Voice Channel")
        else:
            await ctx.author.voice.channel.connect()
            await ctx.send(f"Now playing `Bitch Lasanga` in `{ctx.author.voice.channel.name}`")
            music = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("./db/song1.mp3"))
            await ctx.voice_client.play(music, after=lambda e: print(e) if e else None)
            

    @disstrack.command()
    async def stop(self, ctx):
        if ctx.me.voice is None:
            await ctx.send("Not connected to an voice channel")
        elif len(ctx.me.voice.channel.members) < 2:
            if ctx.author == ctx.guild.owner:
                await ctx.voice_client.disconnect()
                await ctx.send("Disconnected")
            else:
                await ctx.send("There are members in the channel")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected")

def setup(bot):
    bot.add_cog(Music(bot))