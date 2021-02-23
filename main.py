#     TO DO LIST     #
# -> research and implement more moderating commands

import random
import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from discord.ext.commands import MissingRequiredArgument
from discord.ext.commands import NoPrivateMessage

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

DG_dice_list = ['1', '2', '3', '4', '5', '6']
DG_roll_1 = ''
DG_roll_2 = ''
DG_player_1 = ''
DG_player_2 = ''
def DG_reset():
    global DG_roll_1
    global DG_roll_2
    global DG_player_1
    global DG_player_2
    DG_roll_1 = ''
    DG_roll_2 = ''
    DG_player_1 = ''
    DG_player_2 = ''

@client.command()
@commands.guild_only()
async def dice(ctx):
    global DG_roll_1
    global DG_roll_2
    global DG_player_1
    global DG_player_2
    if DG_roll_1 == '' or DG_player_1 == ctx.message.author:
        DG_roll_1 = random.choice(DG_dice_list)
        DG_player_1 = ctx.message.author
        await ctx.send(f'{ctx.message.author.mention} rolled **{DG_roll_1}**!')
    else:
        DG_roll_2 = random.choice(DG_dice_list)
        DG_player_2 = ctx.message.author
        await ctx.send(f'{ctx.message.author.mention} rolled **{DG_roll_2}**!')
        if DG_roll_1 > DG_roll_2:
            await ctx.send(f'{DG_player_1.mention} won!')
            DG_reset()
        elif DG_roll_2 > DG_roll_1:
            await ctx.send(f'{DG_player_2.mention} won!')
            DG_reset()
        else:
            await ctx.send('Tie!')
            DG_reset()

@dice.error
async def dice_error(ctx, error):
    if isinstance(error, NoPrivateMessage):
        print("DM error on .dice")

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
