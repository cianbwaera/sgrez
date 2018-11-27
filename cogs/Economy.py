import discord
import asyncio
import asyncpg
import random
import json
from discord.ext import commands

with open('db/config.json', 'r') as file:
    config = json.load(file)

class PewDieCoin:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['$', 'balance', 'bal'])
    async def bank(self, ctx):
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if count is None:
            count = 0
        await ctx.send(f"You currently have `{count}` coins")

    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command()
    async def timely(self, ctx):
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if count is None:
            count = 0
        await self.bot.db.execute("INSERT INTO bank (user_id, user_money) VALUES ($1, $2 + 75) ON CONFLICT (user_id) DO UPDATE SET user_money= $2 + 75", ctx.author.id, count)
        after_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        await ctx.send(f"Added `75` coins to your coin pouch, your current amount is now `{after_money}` coins")

    @commands.command(alias='cf')
    async def coinflip(self, ctx, side: str, amount_of_coins):
        result = random.choice(['h', 't'])
        amt = amount_of_coins
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if amt == 'all':
            amt = count
        else:
            amt = int(amt)
        if (side == 'head' or side == 'heads') and result == 'h':
            side = 'h'
        elif (side == 'tail' or side == 'tails') and result == 't':
            side = 't'
        else:
            side = side
        if count is None:
            count = 0
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
        author_count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if author_count is None:
            author_count = 0
        if user.bot:
            return await ctx.send("Bot Accounts do not get money")
        if user.id == ctx.author.id:
            return await ctx.send("You cannot give money to yourself")
        if amt > author_count:
            return await ctx.send(f"You have insufficient funds to give to {user.name}")
        else:
            current_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", user.id)
            if current_money is None:
                current_money = 0
            await self.bot.db.execute("UPDATE bank SET user_money = user_money - $1WHERE user_id = $2", amt, ctx.author.id)
            await self.bot.db.execute("INSERT INTO bank (user_id, user_money) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET user_money = $3 + $2", user.id, amt, current_money)
            a = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"I have given {user.mention} `{amt}` coins, You now have {a}"))

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        stats = await self.bot.db.fetch("SELECT * FROM bank ORDER BY user_money DESC LIMIT 5")
        emb = discord.Embed(color=discord.Color(value=0xae2323), title="PewDieCoin Leaderboard - coins")
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        c = 0
        for _ in stats:
            emb.add_field(name=str(self.bot.get_user(stats[c]['user_id']).name), value=f"{stats[c]['user_money']} coins", inline=False)
            c += 1
        await ctx.send(embed=emb)



    @commands.command()
    async def shop(self, ctx):
        roles = await self.bot.db.fetch("SELECT * FROM shop WHERE guild_id=$1", ctx.guild.id)
        emb = discord.Embed(title="PewDieCoin Shop", description="Current roles listed in your server's shop!", color=discord.Color(value=0xae2323))
        c = 0 
        for _ in roles:
            emb.add_field(name=f"#{roles[c]['shop_num']} - {ctx.guild.get_role(roles[c]['role_id']).name}", value=f"{roles[c]['amount']} coins to buy", inline=False)
            c+=1
        emb.set_footer(text="Please report any bugs to my owner | " + config['ver'])
        await ctx.send(embed=emb)

    @commands.command()
    @commands.is_owner()
    async def sell(self, ctx, amount : int, * , role : discord.Role):
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
            await ctx.send(f'```py\n{e}\n```')

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, shop_position : int):
        role = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_position)
        try:
            await self.bot.db.execute("DELETE FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_position)
            await ctx.send(embed=discord.Embed(description=f"{ctx.guild.get_role(role).name} has been removed from the shop!", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(f'```py\n{e}\n```')


    @commands.command()
    async def buy(self, ctx, shop_position : int):
        # Helpers
        role = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_position)
        buyer_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        guild_owner_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.guild.owner.id)
        if buyer_money is None:
            buyer_money = 0
        if guild_owner_money is None:
            guild_owner_money = 0
        role_cost = await self.bot.db.fetchval("SELECT amount FROM shop WHERE shop_num=$1 AND guild_id=$2", shop_position, ctx.guild.id)

        if buyer_money < role_cost:
            return await ctx.send(embed=discord.Embed(description="You have insufficient funds to buy this role", color=discord.Color.red()))
        else:
            await self.bot.db.execute("UPDATE bank SET user_money=$1-$2 WHERE user_id=$3", buyer_money, role_cost, ctx.author.id)
            role_after_taxes = int(round(role_cost - (role_cost * .1)))
            await self.bot.db.execute("INSERT INTO bank(user_id, user_money) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET user_money=$3 + $4", ctx.guild.owner.id, role_after_taxes, guild_owner_money, role_after_taxes)
            await ctx.guild.add_roles(ctx.guild.get_role(role), reason=f"User: {ctx.author.name} bought this")
            await ctx.send(embed=discord.Embed(description=f"Successfully Withdrawed `{role_cost}` coins", color=discord.Color.green()))


def setup(bot):
    bot.add_cog(PewDieCoin(bot))
