import discord, asyncio, json, time, io, traceback, inspect, textwrap, datetime, os, sys, subprocess, copy, typing, aiohttp
from typing import Union
from time import ctime
from contextlib import redirect_stdout
from discord.ext import commands

with open('db/config.json') as bitch:
    config = json.load(bitch)

class OwnerCommands:
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

    @commands.command()
    async def bash(self, ctx, * , cmd : str):
        out = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        content = str(out.stdout.decode('utf-8'))
        if len(content) > 2000:
            fp = io.BytesIO(content.encode('utf-8'))
            return await ctx.send("Can't send full size..", file=discord.File(fp, 'bashresults.txt'))
        if len(content) == '':
            return await ctx.send("Nothing to send..")
        await ctx.send(f"```fix\n{content}\n```")

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
        await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"Unloaded Extension `cogs.{cog}`{config['tickyes']}"))

    @commands.command()
    async def sql(self, ctx, * , query : str):
        # Executes PSQL. Its very unique from others cuz
        # it changes execution from different kws like SELECT because your selecting a value
        t1 = time.perf_counter()
        if ["SELECT",  "select"] in ctx.message.content:
            try:
                meth = await self.bot.db.fetch(query)
            except Exception as e:
                meth = e
        else:
            try:
                meth = await self.bot.db.execute(query)
            except Exception as e:
                meth = e
        e = discord.Embed(title="SQL Query Evaluation",color=discord.Color(value=0xae2323))                
        e.add_field(name="Input :inbox_tray:", value=f"```sql\n{ctx.message.content}\n```", inline=False)
        a.add_field(name="Output :outbox_tray:", value=f'```sql\n{meth}\n```', inline=False)
        t2 = time.perf_counter()
        e.set_footer(text=f"Executed in {round(t2-t1)}ms")
        await ctx.send(embed=e)
            
def setup(bot):
    bot.add_cog(OwnerCommands(bot))
