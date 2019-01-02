import discord
import asyncio
import asyncpg
import random
import json
import string
from datetime import datetime, timedelta
from discord.ext import commands


limit_timely = 50
limit_trade = 9999

class PewDieCoin:
    def __init__(self, bot):
        self.bot = bot
       
    @commands.command(aliases=['$', 'balance', 'bal'])
    async def bank(self, ctx, user : discord.Member=None):
        if not user:
            user = ctx.author
        elif user.id is not self.bot.user.id and user.bot:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"Sorry, but {user.mention} is an bot account which doesn't get coins"))
        else:
            user = user
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", user.id, ctx.guild.id)
        if count is None:
            count = 0

        await ctx.send(embed=discord.Embed(description=f"\uFEFF\n{user.mention} currently has {count:,d} coins", color=discord.Color(value=0xae2323)).set_author(name=str(user), icon_url=user.avatar_url))

    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command()
    async def timely(self, ctx):
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", ctx.author.id, ctx.guild.id)
        if count is None:
            count = 0
 
        a = await self.bot.db.fetchrow("SELECT user_id FROM bank WHERE guild_id=$1 and user_id=$2", ctx.guild.id, ctx.author.id) 
        if a == None:
            await self.bot.db.execute("INSERT INTO bank VALUES($1,$2,$3)", ctx.guild.id, ctx.author.id, limit_timely)
        
        else:
            await self.bot.db.execute("UPDATE bank SET user_money=bank.user_money + $1 WHERE guild_id=$2 and user_id=$3", limit_timely , ctx.guild.id, ctx.author.id)       
        
        after_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", ctx.author.id, ctx.guild.id)

            
        if after_money is None:
            after_money = 0
        await ctx.send(f"Added `{after_money-count}` coins to your coin bank, you now have `{after_money}` coins")

    @commands.command()
    async def rolldice(self, ctx, bet , guess : int):
        money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", ctx.author.id, ctx.guild.id)
        if money is None:
            money = 0
        else:
            money = int(money)
        if bet is None:
            bet = money
        if guess <= 0 or guess > 6 or bet <= 0:
            return await ctx.send(embed=discord.Embed(description="Bet or/and guess is out of range!", color=discord.Color.red()))
        elif bet > money:
            return await ctx.send(embed=discord.Embed(description="You do not have enough funds for this bet", color=discord.Color.red()))
        else:
            result = random.randint(1, 6)
            if result != guess:
                await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"You lost {bet:,d}, better luck next time!"))
                await self.bot.db.execute("UPDATE bank SET user_money = bank.user_money - $1 WHERE user_id=$2 AND guild_id=$3", bet, ctx.author.id, ctx.guild.id)
            else:
                await ctx.send(embed=discord.Embed(description=f"Congrats!, you won `{bet:,d}` coins", color=discord.Color.green()))
                await self.bot.db.execute("UPDATE bank SET user_money = bank.user_money + $1 WHERE user_id=$2 AND guild_id=$3", bet, ctx.author.id, ctx.guild.id)

    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.command()
    async def search(self, ctx):
        is_special = 0
        result = random.randint(0, 40)
        place = random.choice([
            f"You have founded {result} coins in the trash, now i expect you to clean your self up",
            f"An old beggar decided to give you {result + is_special} coins, that is straight up wrong!",
            f"Hmmm, PewDiePie decided to give you {result + is_special} coins. Don't expect to get on the bots good side",
            f"You have founded {result + is_special} in a alley, you smell",
            f"Some robbers drop some coins from thier recent heist, you founded {result + is_special} coins dropped",
            f"An prostitute forgot to pay your {result + is_special} owed coins!"
        ])
        res = await self.bot.db.fetchrow("SELECT user_id FROM bank WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id)
        if res is None:
            await self.bot.db.execute("INSERT INTO bank VALUES($1,$2,$3)", ctx.guild.id, ctx.author.id, result)
        else:
            await self.bot.db.execute("update bank set user_money = user_money + $1 where guild_id=$2 and user_id=$3", result, ctx.guild.id, ctx.author.id)
        await ctx.send(embed=discord.Embed(description=place, color=discord.Color.red()))


    @commands.command(aliases=['cf'])
    async def coinflip(self, ctx, amt, side: str):
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", ctx.author.id, ctx.guild.id)
        if count is None:
            count = 0
        if amt == 'all':
            amt = int(count)
        else:
            amt = int(amt)

        if amt > limit_trade:
            return await ctx.send(embed=discord.Embed(description="You have reached the gambling limit, please gamble a smaller number", color=discord.Color.red()))
        elif amt <= 0:
            return await ctx.send(embed=discord.Embed(description="You cannot give a number that is below or equal to 0", color=discord.Color.red()))

        result = random.choice(['h', 't'])
        side = side.lower()
        if (side == 'head' or side == 'heads' or side == "h"):
            side = 'h'

        elif (side == 'tail' or side == 'tails' or side == "t"):
            side = 't'

        else:
            return await ctx.send(embed=discord.Embed(description=f"{side} is a invalid side!", color=discord.Color.red()))
        
        if amt > count:
            return await ctx.send("Seems like you don't have enough coin")
        else:
            if result == side:
                await ctx.send(embed=discord.Embed(description=f"Congrats fellow Pewd, you won {amt:,d} coins", color=discord.Color.green()))
                await self.bot.db.execute("UPDATE bank SET user_money= bank.user_money + $1 WHERE user_id=$2 AND guild_id=$3", amt, ctx.author.id, ctx.guild.id)
            else:
                await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"You have lost {amt:,d} coins, better luck next time! ^^__^^"))
                await self.bot.db.execute("UPDATE bank SET user_money= bank.user_money - $1 WHERE user_id=$2 AND guild_id=$3", amt, ctx.author.id, ctx.guild.id)

    @commands.command()
    async def give(self, ctx, amt: int, user: discord.Member):
        if amt <= 0:
            return await ctx.send(embed=discord.Embed(description="You cannot give a number that is below or equal to 0", color=discord.Color.red()))
        author_count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", ctx.author.id, ctx.guild.id)
        if author_count is None:
            author_count = 0
        if user.bot:
            return await ctx.send(embed=discord.Embed(description=f"Currently, {user.mention} cannot recieve money due to the user being a Bot Account", color=discord.Color.red()))
        if user.id == ctx.author.id:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), description="Why, why are you trying to give yourself money :thinking:"))
        if amt > author_count:
            return await ctx.send(embed=discord.Embed(description=f"You have insufficient funds to give to {user.name}", color=discord.Color.red()))
        else:
            current_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", user.id, ctx.guild.id)
            if current_money is None:
                current_money = 0
            await self.bot.db.execute("UPDATE bank SET user_money = user_money - $1 WHERE user_id = $2 AND guild_id = $3", amt, ctx.author.id, ctx.guild.id)
            res = await self.bot.db.fetchrow("SELECT user_id FROM bank WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id)
            if res is None:
                await self.bot.db.execute("INSERT INTO bank VALUES($1,$2,$3)", ctx.guild.id, ctx.author.id, amt)
            else:
                await self.bot.db.execute("update bank set user_money = user_money + $1 where guild_id=$2 and user_id=$3", amt, ctx.guild.id, ctx.author.id)
            a = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
            if a is None:
                a = 0
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"I have given {user.mention} `{amt:,d}` coins, You now have {a:,d}"))

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx, want_global=None):
        
        embed = discord.Embed()

        if want_global is None:

            embed.title = f"{ctx.guild.name} Leaderboard"
            embed.description = f"Here, {ctx.author.name}, you can see the list of the top 8 leading people in your server with the most coins!"
            shop = await self.bot.db.fetch("SELECT * FROM bank WHERE guild_id=$1 ORDER BY user_money DESC LIMIT 8", ctx.guild.id)
            embed.color = discord.Color(value=0xae2324)
            counter = 0
            for a in shop:
                counter+=1
                user = self.bot.get_user(a['user_id']).name
                embed.add_field(name=f"#{counter} - {user}", value=f"Holding `{a['user_money']}` coins in their pouch", inline=False)
        elif want_global.lower() == "global":
            embed.title = "Global Leaderboard"
            embed.color = discord.Color(value=0xae2323)
            embed.description = f"Here, {ctx.author.name}, you can find the global top list for all users using pewdiepie!"
            data = await self.bot.db.fetch("SELECT * FROM bank ORDER BY user_money DESC LIMIT 8")

            counter = 0
            for i in data:
                counter+=1
                embed.add_field(name=f"#{counter}: {self.bot.get_user(i['user_id']).name} - {self.bot.get_guild(i['guild_id']).name}", value=f"Currently has {int(i['user_money']):,d} coins in that server", inline=False)
        await ctx.send(embed=embed)
           


    @commands.group()
    @commands.guild_only()
    async def shop(self, ctx):
        if ctx.invoked_subcommand is None:
            # preparing the shop data
            shop_data = await self.bot.db.fetch("SELECT * FROM shop WHERE guild_id=$1", ctx.guild.id)
            embed = discord.Embed(title=f"{ctx.guild.name}'s shop")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            if shop_data == []:
                embed.description = "Your server currently has no roles in the shop"
                embed.color = discord.Color.dark_red()
            else:
                embed.color = discord.Color.dark_green()
                rolecount = len(shop_data)
                if rolecount == 1:
                    rmsg = "role"
                else:
                    rmsg = "roles"
                embed.description = f"{rolecount} {rmsg} has been detected in your server's shop"
                for i in shop_data:
                    embed.add_field(name=f"#{i['shop_id']} - {ctx.guild.get_role(i['role_id']).name}", value=f"Role currently costs `{i['amount']}` coins", inline=False)
                embed.set_footer(text="Thanks for shopping with PewDiePie!")
            await ctx.send(embed=embed)
                


    @shop.command()
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, amount : int, * , role : discord.Role): 
            
        if role.name == "@everyone":
            return await ctx.send(embed=discord.Embed(description="`@everyone` is not allowed, it is a role everyone has..", color=discord.Color.red()))
          
        roles = await self.bot.db.fetch("SELECT * FROM shop WHERE guild_id=$1", ctx.guild.id) # so we wont process over chunks of worthless data
        for i in roles:
            if int(i['role_id']) == int(role.id):
                return await ctx.send(embed=discord.Embed(description=f"Hey, {role.name} is already in the shop, just do `p.shop edit (shop_id) (new amount)` to change its cost", color=discord.Color.red()))
            else:
                continue 

        async def id_gen(role : int):
            going = True
            while going:
                new_id = ''.join(random.choices(string.ascii_uppercase + str(role), k=3))
                if len(roles) == 0:
                    return new_id
                for a in roles:
                    if str(a["shop_id"]) == str(new_id):
                        pass
                    else:
                        going = False
                        print(new_id)
                        return new_id

        result = await id_gen(role.id)
        if ctx.author.top_role.position < role.position:
            return 

        if len(roles) > 8:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), description="Sorry, but your server has reached the maximum limit of roles"))
        else: 
            pass        
        
        if amount > limit_trade:
            return await ctx.send(embed=discord.Embed(description=f"Items Amounts cannot be higher then `{limit_trade}`, please try again", color=discord.Color.red()))
        await self.bot.db.execute("INSERT INTO shop VALUES ($1, $2, $3, $4)", role.id, ctx.guild.id, str(result), int(amount))
        await ctx.send(embed=discord.Embed(description=f"Role: `{role}` has been sold for `{amount}` coins", color=discord.Color.green()))

    @commands.has_permissions(manage_roles=True)
    @shop.command()
    async def remove(self, ctx, shop_id : str):
        role = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_id=$2", ctx.guild.id, shop_id)
        if role is None:
            return await ctx.send(embed=discord.Embed(description=f'Shop Role ID: `{shop_id}` is not in the shop, maybe someone has removed it!', color=discord.Color.red()))
        await self.bot.db.execute("DELETE FROM shop WHERE guild_id=$1 AND shop_id=$2", ctx.guild.id, shop_id)
        await ctx.send(embed=discord.Embed(description=f"Role: `{ctx.guild.get_role(role).name}` has been removed from the shop!", color=discord.Color.green()))

    
    @shop.command()
    @commands.has_permissions(manage_roles=True)
    async def edit(self, ctx, shop_id : int, new_amount : int):
        rid = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_id=$2", ctx.guild.id, shop_id)

        if new_amount > limit_trade:
            await ctx.send(embed=discord.Embed(description=f"`{new_amount}` is over the `{limit_trade}` limit!", color=discord.Color.red()))
        elif rid is None:
            await ctx.send(embed=discord.Embed(description=f"Shop Role ID: `{shop_id}` is not in your shop!", color=discord.Color.red()))
        else:
            await self.bot.db.execute("UPDATE shop SET amount=$1 WHERE role_id=$2 AND guild_id=$3 AND shop_id=$4", new_amount, rid, ctx.guild.id, shop_id)
            await ctx.send(embed=discord.Embed(description=f"Role: `{ctx.guild.get_role(rid).name}` price has been raised to `{new_amount}`"))


    @shop.command()
    async def buy(self, ctx, shop_id : str):
        role = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_id=$2", ctx.guild.id, shop_id)
        for i in ctx.author.roles:
            if i.id == role:
                return await ctx.send(embed=discord.Embed(description="Hmm, it seems if you already have this role, :thinking:", color=discord.Color.red()))
            else:
                continue   
        if ctx.me.top_role.position <= ctx.guild.get_role(role).position:
            return await ctx.send(embed=discord.Embed(description="Seems like i can't give you this role due to my role position, don't panic, your money is not touched", color=discord.Color.red()))
        # Helpers
        buyer_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", ctx.author.id, ctx.guild.id)
        if buyer_money is None:
            buyer_money = 0
        role_cost = await self.bot.db.fetchval("SELECT amount FROM shop WHERE shop_id=$1 AND guild_id=$2", shop_id, ctx.guild.id)

        if buyer_money < role_cost:
            needs = role_cost - buyer_money
            return await ctx.send(embed=discord.Embed(description=f"You have insufficient funds to buy this role, you need {needs:,d} coins to buy it", color=discord.Color.red()))
        else:
            await self.bot.db.execute("UPDATE bank SET user_money=bank.user_money - $1 WHERE user_id=$2 AND guild_id=$3", role_cost, ctx.author.id, ctx.guild.id)
            await ctx.author.add_roles(ctx.guild.get_role(role), reason=f"User: {ctx.author.name} bought this")
            mon = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1 AND guild_id=$2", ctx.author.id, ctx.guild.id)
            await ctx.send(embed=discord.Embed(description=f"Successfully Withdrawed `{role_cost}` coins. You now have {mon:,d} coins", color=discord.Color.green()))


def setup(bot):
    bot.add_cog(PewDieCoin(bot))
