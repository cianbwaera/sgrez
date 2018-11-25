import discord
import asyncio
import asyncpg
import random
from discord.ext import commands
# nothing rn


class PewDieCoin:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['$', 'balance'])
    async def bank(self, ctx):
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if count is None:
            count = 0
        await ctx.send(f"You currently have `{count}` coins")

    @commands.cooldown(1, 14400, commands.BucketType.user)
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
    async def give(self, ctx, amt, user: discord.User):
        author_count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if amt == 'all':
            amt = author_count
        else:
            amt = int(amt)
        if author_count is None:
            author_count = 0
        if user.bot:
            return await ctx.send("Bot Accounts do not get money")
        if user.id == ctx.author.id:
            return await ctx.send("You cannot give money to yourself")
        if amt > author_count:
            return await ctx.send(f"You have insufficient funds to give to {user.name}")
        else:
            current_money = await self.bot.db.fetchval("SELECT * FROM bank WHERE user_id=$1", user.id)
            if current_money is None:
                current_money = 0
            await self.bot.db.execute("""UPDATE bank 
                                         SET user_money = user_money - $1
                                         WHERE user_id = $2""", amt, ctx.author.id)

            await self.bot.db.execute("""INSERT INTO bank (user_id, user_money)
                                         VALUES ($1, $2) ON CONFLICT (user_id)
                                         DO UPDATE 
                                         SET user_money = $3 + $2
                                         """, user.id, amt, current_money)
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"I have given {user.mention} `{amt}` coins, You now have {current_money}"))

    @commands.is_owner()
    @commands.group()
    async def shop(self, ctx):
        """if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=discord.Color.red(), title=f"{ctx.guild}'s Shop", description="Here you will find a list of roles to buy, if none specified, then your server doesnt have the shop set up")
            embed.add_field"""
        pass
    
    @commands.command()
    async def leaderboard(self, ctx):
        stats = await self.bot.db.fetch("SELECT * FROM bank ORDER BY user_money DESC LIMIT 5")
        emb = discord.Embed(color=discord.Color(value=0xae2323), title="Leaderboard for the Most Coins")
        c = 0
        for _ in stats:
            emb.add_field(name=str(self.bot.get_user(stats[c]['user_id']).name), value=f"coins - {stats[c]['user_money']}", inline=False)
            c+=1
        await ctx.send(embed=emb)
        




def setup(bot):
    bot.add_cog(PewDieCoin(bot))
