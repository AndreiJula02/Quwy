#     TO DO LIST     #
# -> research and implement more moderating commands
# -> implement open bets
# -> implement pay, setcredits and other credits related command
# -> add embeds to all the messages

import random
import discord
import sqlite3
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from discord.ext.commands import MissingRequiredArgument

token = 'ODA4MzY0OTc0Mzc5NDk5NTUw.YCFejA.63d1d5v3YzHEWjJw5VMqsYKmiH8'

intents = discord.Intents.all()
client = commands.Bot(command_prefix = 'q.', intents = intents)

#####   BOT STARTUP ANNOUNCEMENT   ###### (functional)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="q.quwyhelp"))
    print('Quwy is up and running')

#####   HELP COMMAND   #####

@client.command()
async def quwyhelp(ctx):
    embed = discord.Embed(title="Quwy", description="Your simple way of enhancing your server!")
    embed.add_field(name="q.invite", value="Generate an invite link that anyone can use to join in the next 2 minutes.")
    embed.add_field(name="q.clear <amount>", value="Deletes the specified amount of messages.")
    embed.add_field(name="q.kick <member>", value="Kicks the mentioned member.")
    embed.add_field(name="q.ban <member>", value="Bans the mentioned member.")
    embed.add_field(name="q.unban <member>", value="Unbans the mentioned member. "
                                                  "Command must be used in the format: q.unban member#1234")
    embed.add_field(name="q.dice", value="Roll the dice! Test your luck by yourself or against a friend.")
    embed.set_footer(text="******\nQuwy is constantly updating and worked on! Current version: 1.0")
    await ctx.send(embed=embed)


#####   DICE ROLL GAME   ##### (functional, to be upgraded)

@client.command()
@commands.guild_only()
async def bet(ctx, enemy2 : discord.Member, amount=0):
    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT Players FROM credits WHERE Players = '{ctx.message.author.id}'")
    result_playerID = cursor.fetchone()
    gameName = "game#" + str(ctx.message.author) + " vs " + str(enemy2)
    if result_playerID is None:
        cursor.execute(f"INSERT INTO credits ('Players') values('{ctx.message.author.id}')")
        db.commit()
    cursor.execute(f"SELECT Players FROM credits WHERE Players = '{enemy2.id}'")
    result_player2ID = cursor.fetchone()
    if result_player2ID is None:
        cursor.execute(f"INSERT INTO credits ('Players') values('{enemy2.id}')")
        db.commit()
    cursor.execute(f"SELECT GameNumber FROM dicebet WHERE GameNumber = '{gameName}'")
    result_gameName = cursor.fetchone()
    if result_gameName is None:
        cursor.execute(f"INSERT INTO dicebet ('GameNumber') values('{gameName}')")
        db.commit()
    cursor.execute(f"UPDATE dicebet SET amount = '{int(amount)}' WHERE GameNumber = ('{gameName}')")
    db.commit()
    cursor.execute(f"SELECT Credits from credits WHERE Players = '{ctx.message.author.id}'")
    result_player1Credits = cursor.fetchone()
    cursor.execute(f"SELECT Credits from credits WHERE Players = '{enemy2.id}'")
    result_player2Credits = cursor.fetchone()
    if int(result_player1Credits[0]) >= int(amount) and int(result_player2Credits[0]) >= int(amount):
        cursor.execute(f"UPDATE dicebet SET player_1 = '{ctx.message.author}' WHERE GameNumber = '{gameName}'")
        cursor.execute(f"UPDATE dicebet SET player_2 = '{enemy2}' WHERE GameNumber = '{gameName}'")
        cursor.execute(f"UPDATE dicebet SET roll_1 = '{random.randint(1,6)}' WHERE GameNumber = '{gameName}'")
        cursor.execute(f"UPDATE dicebet SET roll_2 = '{random.randint(1, 6)}' WHERE GameNumber = '{gameName}'")
        db.commit()
    elif int(result_player1Credits[0]) >= int(amount):
        embed = discord.Embed(title=f"{enemy2} does not have enough credits for that bet.",color=0xff0000)
        await ctx.send(embed=embed)
        cursor.execute(f"DELETE FROM dicebet WHERE GameNumber = '{gameName}'")
        db.commit()
    elif int(result_player2Credits[0]) >= int(amount):
        embed = discord.Embed(title=f"You don't have enough credits for that bet.",color=0xff0000)
        await ctx.send(embed=embed)
        cursor.execute(f"DELETE FROM dicebet WHERE GameNumber = '{gameName}'")
        db.commit()
    else:
        embed = discord.Embed(title=f"Not enough credits.",color=0xff0000)
        await ctx.send(embed=embed)
        cursor.execute(f"DELETE FROM dicebet WHERE GameNumber = '{gameName}'")
        db.commit()

@client.command()
@commands.guild_only()
async def betacc(ctx, enemy1 : discord.Member):
    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    gameName = "game#" + str(enemy1) + " vs " + str(ctx.message.author)
    cursor.execute(f"SELECT GameNumber FROM dicebet WHERE GameNumber = '{gameName}'")
    result_gameName = cursor.fetchone()
    if result_gameName is not None:
        cursor.execute(f"SELECT player_2 FROM dicebet WHERE GameNumber = '{gameName}'")
        result_p2 = cursor.fetchone()
        cursor.execute(f"SELECT player_1 FROM dicebet WHERE GameNumber = '{gameName}'")
        result_p1 = cursor.fetchone()
        cursor.execute(f"SELECT roll_1 FROM dicebet WHERE GameNumber = '{gameName}'")
        result_r1 = cursor.fetchone()
        cursor.execute(f"SELECT roll_2 FROM dicebet WHERE GameNumber = '{gameName}'")
        result_r2 = cursor.fetchone()
        cursor.execute(f"SELECT Credits FROM credits WHERE Players = '{enemy1.id}'")
        result_player1Credits = cursor.fetchone()
        cursor.execute(f"SELECT Credits FROM credits WHERE Players = '{ctx.message.author.id}'")
        result_player2Credits = cursor.fetchone()
        cursor.execute(f"SELECT amount FROM dicebet WHERE GameNumber = '{gameName}'")
        result_amount = cursor.fetchone()
        if int(result_player2Credits[0]) >= int(result_amount[0]) and int(result_player1Credits[0]) >= int(result_amount[0]):
            if str(ctx.message.author) == str(result_p2[0]) and str(enemy1) == str(result_p1[0]):
                if int(result_r1[0]) > int(result_r2[0]):
                    cursor.execute(f"UPDATE credits SET Credits = {int(result_player1Credits[0])} + {int(result_amount[0])} WHERE Players = '{enemy1.id}'")
                    cursor.execute(f"UPDATE credits SET Credits = {int(result_player2Credits[0])} - {int(result_amount[0])} WHERE Players = '{ctx.message.author.id}'")
                    db.commit()
                    embed = discord.Embed(description=f"**{enemy1.name}**-> **{str(result_r1[0])}** vs **{str(result_r2[0])}** <-**{ctx.message.author.name}** | Winner: **{enemy1.name}**",color = 0x00ff08)
                    await ctx.send(embed=embed)
                elif int(result_r2[0]) > int(result_r1[0]):
                    cursor.execute(f"UPDATE credits SET Credits = {int(result_player1Credits[0])} - {int(result_amount[0])} WHERE Players = '{enemy1.id}'")
                    cursor.execute(f"UPDATE credits SET Credits = {int(result_player2Credits[0])} + {int(result_amount[0])} WHERE Players = '{ctx.message.author.id}'")
                    db.commit()
                    embed = discord.Embed(description=f"**{enemy1.name}**-> **{str(result_r1[0])}** vs **{str(result_r2[0])}** <-**{ctx.message.author.name}** | Winner: **{ctx.message.author.name}**",color = 0x00ff08)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=f"**{enemy1.name}**-> **{str(result_r1[0])}** vs **{str(result_r2[0])}** <-**{ctx.message.author.name}** | Tie!",color = 0x00ff08)
                    await ctx.send(embed=embed)
                cursor.execute(f"DELETE FROM dicebet WHERE GameNumber = '{gameName}'")
                db.commit()
            else:
                embed = discord.Embed(title=f"{enemy1} did not bet against you.", color=0xff0000)
                await ctx.send(embed=embed)
        elif int(result_player2Credits[0]) >= int(result_amount[0]):
            embed = discord.Embed(title=f"{str(result_p1[0])} doesn't have enough credits for this bet anymore.", color=0xff0000)
            await ctx.send(embed=embed)
            cursor.execute(f"DELETE FROM dicebet WHERE GameNumber = '{gameName}'")
            db.commit()
        elif int(result_player1Credits[0]) >= int(result_amount[0]):
            embed = discord.Embed(title="You don't have enough credits to accept this bet.", color=0xff0000)
            await ctx.send(embed=embed)
            cursor.execute(f"DELETE FROM dicebet WHERE GameNumber = '{gameName}'")
            db.commit()
        else:
            embed = discord.Embed(title=f"Not enough credits.", color=0xff0000)
            await ctx.send(embed=embed)
            cursor.execute(f"DELETE FROM dicebet WHERE GameNumber = '{gameName}'")
            db.commit()


    else:
        embed = discord.Embed(title=f"{enemy1} doesn't have an open bet.", color=0xff0000)
        await ctx.send(embed=embed)


@client.command()
@commands.guild_only()
@commands.has_permissions(kick_members = True)
async def betremove(ctx, enemy1 : discord.Member, enemy2 : discord.Member):
    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    gameName = "game#" + str(enemy1) + " vs " + str(enemy2)
    cursor.execute(f"SELECT GameNumber FROM dicebet WHERE GameNumber = '{gameName}'")
    result_gameName = cursor.fetchone()
    if result_gameName is not None:
        cursor.execute(f"DELETE FROM dicebet WHERE GameNumber = '{gameName}'")
        db.commit()
        await ctx.send(f"Bet removed.")
    else:
        await ctx.send(f"There is not bet to remove.")

@client.command()
@commands.guild_only()
@commands.has_permissions(administrator = True)
async def betremoveall(ctx):
    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM dicebet")
    db.commit()
    await ctx.send("All bets were removed.")

@client.command()
@commands.guild_only()
async def credits(ctx):
    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT Credits from credits WHERE Players = '{ctx.message.author.id}'")
    result_credits = cursor.fetchone()
    if result_credits is not None:
        embed = discord.Embed(description=f":coin: You have **{str(result_credits[0])}** credits! :coin:",color=0xffee00)
        embed.set_footer(text=f"{ctx.message.author}")
        await ctx.send(embed=embed)
    else:
        cursor.execute(f"INSERT INTO credits ('Players') values('{ctx.message.author.id}')")
        db.commit()
        cursor.execute(f"SELECT Credits from credits WHERE Players = '{ctx.message.author.id}'")
        result_credits = cursor.fetchone()
        embed = discord.Embed(description=f":coin: You have **{str(result_credits[0])}** credits! :coin:",color=0xffee00)
        embed.set_footer(text=f"{ctx.message.author}")
        await ctx.send(embed=embed)


#####   CLEAR COMMAND   ##### (functional)

@client.command()
@commands.guild_only()
@commands.has_permissions(manage_messages = True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit = amount+1)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You do not have the permission to delete messages.")
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Please use: **q.clear <amount>**")


#####   INVITE COMMAND   ##### (functional)

@client.command()
@commands.guild_only()
async def invite(ctx):
    link = await ctx.channel.create_invite(max_age=120)
    await ctx.send(f"Use this to invite people on this server, it will expire after 2 minutes: ")
    await ctx.send(link)

#####   KICK COMMAND   ##### (functional)

@client.command()
@commands.guild_only()
@commands.has_permissions(kick_members = True)
async def kick(ctx, member : discord.Member, *, reason = "No reason"):
    await member.kick(reason = reason)
    await ctx.send(f'{member} was kicked. Reason: "{reason}".')

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You do not have the permission to kick members.")
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Please use: **q.kick <member>**")

#####   BAN COMMAND   ##### (functional)

@client.command()
@commands.guild_only()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = "No reason"):
    await member.ban(reason = reason)
    await ctx.send(f'{member} was banned. Reason: "{reason}".')

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You do not have the permission to ban members.")
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Please use: **q.ban <member>**")

#####   UNBAN COMMAND   ##### (functional)

@client.command()
@commands.guild_only()
@commands.has_permissions(ban_members = True)
async def unban(ctx, *, member):
    try:
        ban_list = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in ban_list:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"{user.mention} was unbanned.")
                return
    except ValueError:
        await ctx.send(f"Couldn't find {member}," 
                       f" make sure you're using the command correctly, e.g. **q.unban andrei02#0216**")

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You do not have the permission to unban members.")
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Please use: **q.unban <member>**, e.g. _q.unban andrei02#0216_")

client.run(token)
