import discord
import asyncio
import asyncpg
import random
import json
from datetime import datetime, timedelta
from discord.ext import commands

with open('db/config.json', 'r') as file:
    config = json.load(file)

class PewDieCoin:
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.cooldowns_task())

    def __unload(self):
        self.task.cancel()

    async def add_cooldown(self, timer : int, user_id: int):
        try:
            await self.bot.db.execute("INSERT INTO cooldowns VALUES($1,$2)", user_id, timer)
        except:
            return
   
    async def cooldowns_task(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            users = await self.bot.db.fetch("SELECT * FROM cooldowns ORDER BY end_time")
            for a in users:
                if a["end_time"] <= 0:
                    await self.bot.db.execute("DELETE FROM cooldowns WHERE user_id=$1", int(a["user_id"]))
                else:
                    await self.bot.db.execute("UPDATE cooldowns SET end_time=cooldowns.end_time - 1 WHERE user_id=$1", int(a['user_id']))
                awai
        
    async def get_cooldown(self, user:int):
        cd = await self.bot.db.fetchval("SELECT end_time FROM cooldowns WHERE user_id=$1",user)
        if cd is None:
            cd = 0
        return cd
        
    @commands.command(aliases=['$', 'balance', 'bal'])
    async def bank(self, ctx):
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if count is None:
            count = 0
        await ctx.send(f"You currently have `{count}` coins")


    @commands.command()
    async def timely(self, ctx):
        a = await self.get_cooldown(ctx.author.id)
        if a != 0:
            seconds = int(a)
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            return await ctx.send(embed=discord.Embed(color=discord.Color(value=0xae2323), title="Already recieved!", description=f"You already claimed your timely reward, try again in **{hours}**hrs, **{minutes}**m, **{seconds}**s"))
        else:
            await self.add_cooldown(timer=3600, user_id=ctx.author.id)
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if count is None:
            count = 0
        await self.bot.db.execute("INSERT INTO bank (user_id, user_money) VALUES ($1, $2 + 75) ON CONFLICT (user_id) DO UPDATE SET user_money= $2 + 75", ctx.author.id, count)
        after_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        await ctx.send(f"Added `75` coins to your coin bank, you now have `{after_money}` coins")

    @commands.command()
    async def rolldice(self, ctx, bet : int, guess : int):
        money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if money is None:
            money = 0
        else:
            money = int(money)
        if guess <= 0 or guess > 6 or bet <= 0:
            return await ctx.send(embed=discord.Embed(description="Invalid roll/bet! Please make sure you're doing\n`p.rolldice (bet) (side guess)`", color=discord.Color.red()))
        elif bet > money:
            return await ctx.send(embed=discord.Embed(description="You do not have enough funds for this bet", color=discord.Color.red()))
        else:
            result = random.randint(1, 6)
            if result != guess:
                await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"So sad, you lost `{bet}` coins lolol"))
                await self.bot.db.execute("UPDATE bank SET user_money = bank.user_money - $1 WHERE user_id=$2", bet, ctx.author.id)
            else:
                await ctx.send(embed=discord.Embed(description=f"Congrats!, you won `{bet}` coins", color=discord.Color.green()))
                await self.bot.db.execute("UPDATE bank SET user_money = bank.user_money + $1 WHERE user_id=$2", bet, ctx.author.id)


    @commands.command(aliases=['cf'])
    async def coinflip(self, ctx, amount_of_coins, side: str,):
        amt = amount_of_coins
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if count is None:
            count = 0
        if amt == 'all':
            amt = int(count)
        else:
            amt = int(amt)
        if amt <= 0:
            return await ctx.send(embed=discord.Embed(description="You cannot give an negative amount", color=discord.Color.red()))
        result = random.choice(['h', 't'])
        
        if (side == 'head' or side == 'heads') and result == 'h':
            side = 'h'
        elif (side == 'tail' or side == 'tails') and result == 't':
            side = 't'
        else:
            side = side
        
        if amt > count:
            return await ctx.send("Seems like you don't have enough coin")
        else:
            if result == side:
                await ctx.send(embed=discord.Embed(description=f"Congrats fellow Pewd, you won {amt} coins", color=discord.Color.green()))
                await self.bot.db.execute("UPDATE bank SET user_money= user_money + $1 WHERE user_id=$2", amt, ctx.author.id)
            else:
                await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"Lost to T-Series by {amt} coins"))
                await self.bot.db.execute("UPDATE bank SET user_money= user_money - $1 WHERE user_id=$2", amt, ctx.author.id)

    @commands.command()
    async def give(self, ctx, amt: int, user: discord.User):
        if amt <= 0:
            return await ctx.send(embed=discord.Embed(description="You cannot give an negative amount to someone", color=discord.Color.red()))
        author_count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if author_count is None:
            author_count = 0
        if user.bot:
            return await ctx.send(embed=discord.Embed(description="Bot accounts do not get money", color=discord.Color.red()))
        if user.id == ctx.author.id:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), description="You cannot give money to yourself"))
        if amt > author_count:
            return await ctx.send(embed=discord.Embed(description=f"You have insufficient funds to give to {user.name}", color=discord.Color.red()))
        else:
            current_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", user.id)
            if current_money is None:
                current_money = 0
            await self.bot.db.execute("UPDATE bank SET user_money = user_money - $1 WHERE user_id = $2", amt, ctx.author.id)
            await self.bot.db.execute("INSERT INTO bank (user_id, user_money) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET user_money = $3 + $2", user.id, amt, current_money)
            a = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
            if a is None:
                a = 0
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"I have given {user.mention} `{amt}` coins, You now have {a}"))

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        stats = await self.bot.db.fetch("SELECT * FROM bank ORDER BY user_money DESC LIMIT 5")
        emb = discord.Embed(color=discord.Color(value=0xae2323), title="Global Leaderboard - coins")
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        c = 0
        for _ in stats:
            emb.add_field(name=str(self.bot.get_user(stats[c]['user_id']).name), value=f"{stats[c]['user_money']} coins", inline=False)
            c += 1
        await ctx.send(embed=emb)

    @commands.group()
    async def shop(self, ctx):
        if ctx.invoked_subcommand is None:
            roles = await self.bot.db.fetch("SELECT * FROM shop WHERE guild_id=$1", ctx.guild.id)
            if str(roles) == '[]':
                bio = "Your server currently has no roles to buy at the moment, try asking a moderator to add some"
            else:
                bio = "Here's some roles you can buy, buy them by `p.shop buy number`\n\uFEFF\n"
            emb = discord.Embed(description=bio, color=discord.Color(value=0xae2323))
            
            emb.set_author(name=f"{ctx.guild.name}'s Shop")
            
            c = 0 
            for _ in roles:
                emb.add_field(name=f"#{roles[c]['shop_num']} - {ctx.guild.get_role(roles[c]['role_id']).name}", value=f"`{roles[c]['amount']}` coins to buy", inline=False)
                c+=1
            emb.set_thumbnail(url=ctx.guild.icon_url)
            emb.add_field(name='\uFEFF', value="\uFEFF")
            emb.set_footer(text="PewDieCoin | " + config['ver'])
            await ctx.send(embed=emb)

    @shop.command()
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, amount : int, * , role : discord.Role): 
        roles = await self.bot.db.fetch("SELECT * FROM shop WHERE guild_id=$1", ctx.guild.id)
        for i in roles:
            if i['role_id'] == role.id:
                return
            else:
                continue   
        if ctx.author.top_role.position < role.position:
            return
        shop_pos = await self.bot.db.fetchval("SELECT COUNT(*) FROM shop WHERE guild_id=$1", ctx.guild.id)
        if shop_pos is None:
            shop_pos = 0
        shop_pos+=1
        if amount > 9999:
            return await ctx.send(embed=discord.Embed(description="Items Amounts cannot be higher then `9999`, please try again", color=discord.Color.red()))
        try:
            await self.bot.db.execute('INSERT INTO shop VALUES($1,$2,$3,$4);', role.id, ctx.guild.id,shop_pos, amount)
            await ctx.send(embed=discord.Embed(description=f"Role: `{role}` has been sold for `{amount}` coins", color=discord.Color.green()))
        except Exception as e:
            print(e)

    @commands.has_permissions(manage_roles=True)
    @shop.command()
    async def remove(self, ctx, shop_position : int):
        role = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_position)
        try:
            await self.bot.db.execute("DELETE FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_position)
            await ctx.send(embed=discord.Embed(description=f"Role: `{ctx.guild.get_role(role).name}` has been removed from the shop!", color=discord.Color.green()))
        except Exception as e:
            print(e)


    @shop.command()
    async def buy(self, ctx, shop_position : int):
        role = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_position)
        for i in ctx.author.roles:
            if i.id == role:
                return
            else:
                continue   
        if ctx.me.top_role.position <= ctx.guild.get_role(role).position:
            return await ctx.send(embed=discord.Embed(description="Seems like i can't give you this role due to my role position, don't panic, your money is not touched", color=discord.Color.red()))
        # Helpers
        buyer_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if buyer_money is None:
            buyer_money = 0
        role_cost = await self.bot.db.fetchval("SELECT amount FROM shop WHERE shop_num=$1 AND guild_id=$2", shop_position, ctx.guild.id)

        if buyer_money < role_cost:
            return await ctx.send(embed=discord.Embed(description="You have insufficient funds to buy this role", color=discord.Color.red()))
        else:
            await self.bot.db.execute("UPDATE bank SET user_money=user_money - $1 WHERE user_id=$2", role_cost, ctx.author.id)
            await ctx.author.add_roles(ctx.guild.get_role(role), reason=f"User: {ctx.author.name} bought this")
            await ctx.send(embed=discord.Embed(description=f"Successfully Withdrawed `{role_cost}` coins", color=discord.Color.green()))


def setup(bot):
    bot.add_cog(PewDieCoin(bot))
