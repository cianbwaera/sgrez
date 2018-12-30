import discord, asyncio, json, time, io, traceback, inspect, textwrap, datetime, os, sys, subprocess, copy, typing, aiohttp, random
from typing import Union
from time import ctime
from contextlib import redirect_stdout
from discord.ext import commands


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
            'msg': ctx.message,
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
        else:
            value = stdout.getvalue()
          

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
               

    @commands.command(aliases=['rl'])
    async def reload(self, ctx, cog=None):
        cogs = self.bot.config['cogs']
        if not cog:
            try:
                for module in cogs:
                    self.bot.unload_extension("modules." + module)
                    self.bot.load_extension("modules." + module)
                return await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"Successfully Reloaded {len(cogs)} Extensions {self.bot.config['tickyes']}"))            
            except Exception as e:
                return await ctx.send(embed=discord.Embed(description=f"Could Not Reload {len(module)} Extensions {self.bot.config['tickno']}\n```bash\n{e}\n```", color=discord.Color.red()))
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"Successfully Reloaded `{cog}` {self.bot.config['tickyes']}"))            
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"Could Not Reload `modules.{cog}` {self.bot.config['tickno']}\n```bash\n{e}\n```", color=discord.Color.red()))

    @commands.command()
    async def bash(self, ctx, * , cmd : str):
        proc = subprocess.Popen(['/bin/bash', "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate(timeout=30)
        content = f"\n-- input --\n\n\nenter@enn-vps:~/$ {cmd}\n\n\n-- stdout --\n\n\n"+ str(out.decode('utf-8')) + "\n\n-- stderr --\n\n\n"+ str(err.decode('utf-8')) + "\n"
        try:
            await ctx.send(f"```bash{content}```")
        except discord.HTTPException:
            content = content.replace("```","")
            msg = await ctx.send("Output too long, uploading to Hastebin..")
            try:
                async with aiohttp.ClientSession().post("https://hastebin.com/documents/", data=content.encode()) as resq:
                    a = await resq.json()
                    a = a['key']
                    url = f"https://hastebin.com/" + a
                    await msg.edit(content=f"Uploaded to Hastebin: {url}")
            except Exception as error:
                await msg.edit(content="Slight error, \n{}".format(error))

    @commands.command(aliases=['l'])
    async def load(self, ctx, cog):
        try:
            self.bot.load_extension(cog)
            await ctx.send(embed=discord.Embed(description=f"Loaded Extension `modules.{cog}` {self.bot.config['tickyes']}", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"Could Not Load Extension: `modules.{cog}` {self.bot.config['tickno']}\n```fix\n{e}\n```"))

    @commands.command(aliases=['ul'])
    async def unload(self, ctx, cog):
        self.bot.unload_extension(cog)
        await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"Unloaded Extension `modules.{cog}` {self.bot.config['tickyes']}"))

    @commands.command()
    async def sql(self, ctx, * , query : str):
        try:
           meth = await self.bot.db.fetch(query)
        except Exception as e:
            meth = e
        e = discord.Embed(title="SQL Query Evaluation",color=discord.Color(value=0xae2323))                
        e.add_field(name=":inbox_tray: Input", value=f"```sql\n{query}\n```", inline=False)
        e.add_field(name=":outbox_tray: Output" , value=f'```sql\n{meth}\n```', inline=False)
        await ctx.send(embed=e)


    @commands.command()
    async def update(self, ctx, * , annoucement):
        await self.bot.db.execute("INSERT INTO development(updates, rid) VALUES($1, 1) ON CONFLICT(rid) DO UPDATE SET updates=$1", annoucement)
        await ctx.send("Successfully updated")
            
def setup(bot):
    bot.add_cog(Developer_Tools(bot))
