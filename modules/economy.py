import discord
import asyncio
import asyncpg
import random
import json
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
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", user.id)
        if count is None:
            count = 0
        await ctx.send(embed=discord.Embed(title=f"{user.name}'s Balance", description=f"{user.mention} currently has {count:,d} coins", color=discord.Color(value=0xae2323)))

    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command()
    async def timely(self, ctx):
        is_special = await self.bot.db.fetchval("SELECT coin_award FROM giveaways WHERE user_id=$1", ctx.author.id)
        if is_special is None:
            is_special = 0
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if count is None:
            count = 0
        # There is a reason why i have f-strings for this statement
        await self.bot.db.execute(f"INSERT INTO bank (user_id, user_money) VALUES ($1, $2 + {limit_timely + is_special}) ON CONFLICT (user_id) DO UPDATE SET user_money= $2 + {limit_timely + is_special}", ctx.author.id, count)
        after_money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        await ctx.send(f"Added `{after_money-count}` coins to your coin bank, you now have `{after_money}` coins")

    @commands.command()
    async def rolldice(self, ctx, bet , guess : int):
        money = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
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
                await self.bot.db.execute("UPDATE bank SET user_money = bank.user_money - $1 WHERE user_id=$2", bet, ctx.author.id)
            else:
                await ctx.send(embed=discord.Embed(description=f"Congrats!, you won `{bet:,d}` coins", color=discord.Color.green()))
                await self.bot.db.execute("UPDATE bank SET user_money = bank.user_money + $1 WHERE user_id=$2", bet, ctx.author.id)

    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.command()
    async def search(self, ctx):
        is_special = await self.bot.db.fetchval("SELECT coin_award FROM giveaways WHERE user_id=$1", ctx.author.id)
        if is_special is None:
            is_special = 0
        # c
        result = random.randint(0, 40)
        place = random.choice([
            f"You have founded {result} coins in the trash, now i expect you to clean your self up",
            f"An old beggar decided to give you {result + is_special} coins, that is straight up wrong!",
            f"Hmmm, PewDiePie decided to give you {result + is_special} coins. Don't expect to get on the bots good side",
            f"You have founded {result + is_special} in a alley, you smell",
            f"Some robbers drop some coins from thier recent heist, you founded {result + is_special} coins dropped",
            f"An prostitute forgot to pay your {result + is_special} owed coins!"
        ])
        await self.bot.db.execute(f"INSERT INTO bank(user_id, user_money) VALUES($1,$2) ON CONFLICT(user_id) DO UPDATE SET user_money=bank.user_money+$2",ctx.author.id, result + is_special)

        await ctx.send(embed=discord.Embed(description=place, color=discord.Color.red()))


    @commands.command(aliases=['cf'])
    async def coinflip(self, ctx, amt, side: str):
        count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
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
        # to make it case insensitive
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
                await self.bot.db.execute("UPDATE bank SET user_money= user_money + $1 WHERE user_id=$2", amt, ctx.author.id)
            else:
                await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"You have lost {amt:,d} coins, better luck next time! ^^__^^"))
                await self.bot.db.execute("UPDATE bank SET user_money= user_money - $1 WHERE user_id=$2", amt, ctx.author.id)

    @commands.command()
    async def give(self, ctx, amt: int, user: discord.Member):
        if amt <= 0:
            return await ctx.send(embed=discord.Embed(description="You cannot give a number that is below or equal to 0", color=discord.Color.red()))
        author_count = await self.bot.db.fetchval("SELECT user_money FROM bank WHERE user_id=$1", ctx.author.id)
        if author_count is None:
            author_count = 0
        if user.bot:
            return await ctx.send(embed=discord.Embed(description=f"Currently, {user.mention} cannot recieve money due to the user being a Bot Account", color=discord.Color.red()))
        if user.id == ctx.author.id:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), description="Why, why are you trying to give yourself money :thinking:"))
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
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=f"I have given {user.mention} `{amt:,d}` coins, You now have {a:,d}"))

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        stats = await self.bot.db.fetch("SELECT * FROM bank ORDER BY user_money DESC LIMIT 8")
        emb = discord.Embed(color=discord.Color(value=0xae2323), title="Global Leaderboard - coins")
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        c = 0
        for _ in stats:
            if stats[c]['user_id'] is not None:
                emb.add_field(name=self.bot.get_user(stats[c]['user_id']).name, value=f"Currently has {(stats[c]['user_money']):,d} coins", inline=False)
                c+=1
            else:
                c+=1
                
        emb.set_footer(text="\uFEFF")
        await ctx.send(embed=emb)
   
    @commands.group()
    async def shop(self, ctx):
        if ctx.invoked_subcommand is None:
            roles = await self.bot.db.fetch("SELECT * FROM shop WHERE guild_id=$1 ORDER BY shop_num", ctx.guild.id)
            if roles == []:
                bio = "Your server currently has no available roles to buy right now"
            else:
                bio = f"Here's some roles you can buy in {ctx.guild}\n\uFEFF\n"
            emb = discord.Embed(description=bio, color=discord.Color(value=0xae2323))
            
            emb.set_author(name=f"{ctx.guild.name}'s Shop")
            
            c = 0 
            for _ in roles:
                emb.add_field(name=f"#{roles[c]['shop_num']} - {ctx.guild.get_role(roles[c]['role_id']).name}", value=f"Role costs `{roles[c]['amount']}` coins, buy it by `p.shop buy {roles[c]['shop_num']}`", inline=False)
                c+=1
            emb.set_thumbnail(url=ctx.guild.icon_url)
            emb.add_field(name='\uFEFF', value="\uFEFF")
            emb.set_footer(text=self.bot.config['ver'])
            await ctx.send(embed=emb)

    @shop.command()
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, amount : int, * , role : discord.Role): 
        if role.name == "@everyone":
            return await ctx.send(embed=discord.Embed(description="`@everyone` is not allowed, it is a role everyone has..", color=discord.Color.red()))
          
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

        if len(roles) > 8:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), description="Sorry, but your server has reached the maximum limit of roles"))
        else: 
            pass        
        
        if amount > limit_trade:
            return await ctx.send(embed=discord.Embed(description=f"Items Amounts cannot be higher then `{limit_trade}`, please try again", color=discord.Color.red()))
        try:
            await self.bot.db.execute('INSERT INTO shop VALUES($1,$2,$3,$4);', role.id, ctx.guild.id,shop_pos, amount)
            await ctx.send(embed=discord.Embed(description=f"Role: `{role}` has been sold for `{amount}` coins", color=discord.Color.green()))
        except Exception as e:
            print(e)

    @commands.has_permissions(manage_roles=True)
    @shop.command()
    async def remove(self, ctx, shop_position : int):
        role = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_position)
        if role is None:
            return await ctx.send(embed=discord.Embed(description=f'Role: `{shop_position}` is not in the shop, maybe someone has removed it!', color=discord.Color.red()))
        await self.bot.db.execute("DELETE FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_position)
        await ctx.send(embed=discord.Embed(description=f"Role: `{ctx.guild.get_role(role).name}` has been removed from the shop!", color=discord.Color.green()))

    
    @shop.command()
    @commands.has_permissions(manage_roles=True)
    async def edit(self, ctx, shop_pos : int, new_amount : int):
        rid = await self.bot.db.fetchval("SELECT role_id FROM shop WHERE guild_id=$1 AND shop_num=$2", ctx.guild.id, shop_pos)

        if new_amount > limit_trade:
            await ctx.send(embed=discord.Embed(description=f"`{new_amount}` is over the `{limit_trade}` limit!", color=discord.Color.red()))
        elif rid is None:
            await ctx.send(embed=discord.Embed(description=f"`{shop_pos}` is not in your shop!", color=discord.Color.red()))
        else:
            await self.bot.db.execute("UPDATE shop SET amount=$1 WHERE role_id=$2 AND guild_id=$3 AND shop_num=$4", new_amount, rid, ctx.guild.id, shop_pos)
            await ctx.send(embed=discord.Embed(description=f"Role: `{ctx.guild.get_role(rid).name}` price has been raised to `{new_amount}`"))


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
