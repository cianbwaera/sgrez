import discord, asyncio, json, time, io, traceback, inspect, textwrap, datetime, os, sys, subprocess, copy, typing, aiohttp
from typing import Union
from time import ctime
from contextlib import redirect_stdout
from discord.ext import commands

with open('db/config.json') as bitch:
    config = json.load(bitch)

class Developer_Tools:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, message):
        if message.startswith('```') and message.startswith("```"):
            return "\n".join(message.split('\n')[1:-1])
        return message.strip(' \n')
    
    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command()
    async def eval(self, ctx, *, body : str):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            "db" : self.bot.db,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}```')
            try:
                await ctx.message.add_reaction(config['ticknoreact'])
            except:
                pass
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction(config['tickyesreact'])
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command(aliases=['rl'])
    async def reload(self, ctx, cog=None):
        cogs = config['cogs']
        if not cog:
            try:
                for module in cogs:
                    self.bot.unload_extension("cogs."+ module)
                    self.bot.load_extension("cogs." + module)
                return await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"Successfully Reloaded {len(cogs)} Extensions {config['tickyes']}"))            
            except Exception as e:
                return await ctx.send(embed=discord.Embed(description=f"Could Not Reload {len(module)} Extensions {config['tickno']}\n```bash\n{e}\n```", color=discord.Color.red()))
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"Successfully Reloaded `cogs.{cog}` {config['tickyes']}"))            
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"Could Not Reload `cogs.{cog}` {config['tickno']}\n```bash\n{e}\n```", color=discord.Color.red()))

    @commands.group()
    async def blacklist(self, ctx):
        pass

    @blacklist.command()
    async def guild(self, ctx, id : int):
        check_if_is = await self.bot.db.fetchval("SELECT result FROM blacklisted_guilds WHERE guild_id=$1", id)
        if check_if_is is None:
            await self.bot.db.execute("INSERT INTO blacklisted_guilds VALUES($1,$2) ON CONFLICT(guild_id) DO NOTHING", id,"dwqdwqdwq")
            await ctx.send(embed=discord.Embed(description=f"Successfully blacklisted {self.bot.get_guild(id).name}, i will leave the guild if its in my guild list", color=discord.Color.green()))
            for i in self.bot.guilds:
                if i.id == id:
                    await i.leave()
                else:
                    continue
        else:
            await ctx.send(embed=discord.Embed(description="This server is already blacklisted!", color=discord.Color.red()))

    @commands.group()
    async def unblacklist(self,ctx):
        pass
    
    @unblacklist.command(name="guild")
    async def g(self, ctx, id : int):
        is_it_there = await self.bot.db.fetchval("SELECT result FROM blacklisted_guilds WHERE guild_id=$1", id)
        if is_it_there is None:
            return await ctx.send(embed=discord.Embed(description="Server isn't currently blacklisted", color=discord.Color.red()))
        else:
            await self.bot.db.execute("DELETE FROM blacklisted_guilds WHERE guild_id=$1",id)
            await ctx.send(embed=discord.Embed(description=f"Successfully unblacklisted guild", color=discord.Color.green()))

    @commands.command()
    async def bash(self, ctx, * , cmd : str):
        proc = subprocess.Popen(['/bin/bash', "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate(timeout=120)
        content = f"\n-- input --\n\n\n{cmd}\n\n\n-- stdout --\n\n\n"+ str(out.decode('utf-8')) + "\n\n-- stderr --\n\n\n"+ str(err.decode('utf-8')) + "\n"
        try:
            await ctx.send(f"```fix{content}```")
        except discord.HTTPException:
            content = content.replace("```","")
            msg = await ctx.send("Output too long, uploading to Hastebin..")
            async with aiohttp.ClientSession().post("https://hastebin.com/documents/", data=content.encode()) as resq:
                a = await resq.json()
                a = a['key']
                url = f"https://hastebin.com/" + a
                await msg.edit(content=f"Uploaded to Hastebin: {url}")
            
        

    @commands.command(aliases=['l'])
    async def load(self, ctx, cog):
        try:
            self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(embed=discord.Embed(description=f"Loaded Extension `cogs.{cog}` {config['tickyes']}", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"Could Not Load Extension: `cogs.{cog}` {config['tickno']}\n```fix\n{e}\n```"))

    @commands.command(aliases=['ul'])
    async def unload(self, ctx, cog):
        self.bot.unload_extension(f"cogs.{cog}")
        await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"Unloaded Extension `cogs.{cog}` {config['tickyes']}"))

    @commands.command()
    async def sql(self, ctx, * , query : str):
        if "SELECT" or "select" in ctx.message.content:
            try:
                meth = await self.bot.db.fetch(query)
            except discord.HTTPException:
                meth = "2000 word limit"
            except Exception as e:
                meth = e
        else:
            try:
                await self.bot.db.execute(query)                
                meth = 'Executed!'
            except Exception as e:
                meth = e
        e = discord.Embed(title="SQL Query Evaluation",color=discord.Color(value=0xae2323))                
        e.add_field(name=":inbox_tray: Input", value=f"```sql\n{query}\n```", inline=False)
        e.add_field(name=":outbox_tray: Output" , value=f'```sql\n{meth}\n```', inline=False)
        await ctx.send(embed=e)
            
def setup(bot):
    bot.add_cog(Developer_Tools(bot))
