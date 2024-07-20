import disnake
import mysql.connector
from disnake.ext import commands
import music_func
from mysql.connector import connect, Error
import functools
import itertools
import math
import random
import asyncio
from disnake import Activity, ActivityType
import youtube_dl
from async_timeout import timeout

#connect to databases
try:
    with connect(
        host="localhost",
        user="your name",
        password="your password",
        database="MPG",
    ) as connection:
        print("You're connected to MySQL")
except Error as e:
    print(e)
#local connection(spec)
cnn = mysql.connector.connect(host="localhost",user="your name",password="your password",database="MPG",)

cursor = cnn.cursor()
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='>', intents=intents, test_guilds=['your guild id'])

#work with rection events
@bot.event
async def on_raw_reaction_add(payload: disnake.RawReactionActionEvent):
    """Gives a role based on a reaction emoji."""
    guild = bot.get_guild(payload.guild_id)
    gid = str(guild.id) + '_emoji'
    print(gid)
    wehave = "SELECT * FROM {gi} WHERE emo=%s"
    cursor.execute(wehave.format(gi=gid), ('emo_msg',))
    role_message_id = cursor.fetchall()
    wehave = "SELECT * FROM {gi} WHERE user_id=%s"
    cursor.execute(wehave.format(gi=gid+'_req'), (payload.user_id,))
    req_check = cursor.fetchall()
    
    #check reqests to takes new dependeces for reactions
    if req_check !=[]:
        if payload.message_id!=req_check[0][1]:
            return
        wehave = "SELECT * FROM {gi} WHERE emo=%s"
        cursor.execute(wehave.format(gi=gid), (str(payload.emoji),))
        emo_check = cursor.fetchall()
        if emo_check !=[]:
            upd_emo_link = """UPDATE {gi} SET rol=%s WHERE emo=%s"""
            cursor.execute(upd_emo_link.format(gi=gid), (req_check[0][2], str(payload.emoji),))
            cnn.commit()
        else:
            insert_req = """INSERT INTO {g} (emo,rol) VALUES (%s,%s)"""
            cursor.execute(insert_req.format(g=gid), (str(payload.emoji),req_check[0][2]))
            cnn.commit()
        sql = "DELETE FROM {g} WHERE user_id = %s".format(g=gid+'_req')
        cursor.execute(sql,(payload.user_id,))
        cnn.commit()
    if payload.message_id != role_message_id[0][1]:
        # check mess what we need
        return
    if guild is None:
        # check if we're still in the guild and it's cached.
        return
    # try to give the role
    try:
        gid = str(guild.id)+'_emoji'
        wehave = "SELECT * FROM {gi} WHERE emo=%s"
        cursor.execute(wehave.format(gi = gid), (str(payload.emoji),))
        role_id = cursor.fetchall()
    except KeyError:
        # if the emoji isn't the one we care about then exit as well.
        return
    role = guild.get_role(role_id[0][1])
    if role is None:
        # make sure the role still exists and is valid.
        return
    try:
        await payload.member.add_roles(role)
    except disnake.HTTPException:
        print("No role added")
        pass

#swap main message to role dispencer
@bot.slash_command(description="update message(id) which have emoji to role func")
async def upd_emo_msg(inter: disnake.ApplicationCommandInteraction,message_id):
    guild = bot.get_guild(inter.guild_id)
    gid = str(guild.id) + '_emoji'
    upda_emo_msg = """UPDATE {gi} SET rol=%s WHERE emo=%s"""
    cursor.execute(upda_emo_msg.format(gi=gid), (int(message_id),'emo_msg',))
    cnn.commit()
    await inter.response.send_message("Successfully updated",ephemeral=True,delete_after=10)

#command make assciation role to emoj
@bot.slash_command(description="update message(id) which have emoji to role func")
async def link_emo_rol(inter: disnake.ApplicationCommandInteraction,role_id):
    guild = bot.get_guild(inter.guild_id)
    gid = str(guild.id) + '_emoji'
    await inter.response.send_message("Put sought-for emoji to this message(for {aut})".format(aut=inter.author.name),delete_after=30)
    msg = message = await inter.original_response()
    insert_req = """INSERT IGNORE INTO {g} (user_id,message_id,role_id) VALUES (%s,%s,%s)"""
    cursor.execute(insert_req.format(g=gid+'_req'), (inter.author.id,msg.id,role_id))
    cnn.commit()
@bot.event


async def on_raw_reaction_remove(payload: disnake.RawReactionActionEvent):
    """Removes a role based on a reaction emoji."""
    guild = bot.get_guild(payload.guild_id)
    gid = str(guild.id) + '_emoji'
    wehave = "SELECT * FROM {gi} WHERE emo=%s"
    cursor.execute(wehave.format(gi=gid), ('emo_msg',))
    role_message_id = cursor.fetchall()
    if payload.message_id != role_message_id[0][1]:
        return
    if guild is None:
        # check if we're still in the guild and it's cached.
        return

    try:
        gid = str(guild.id) + '_emoji'
        wehave = "SELECT * FROM {gi} WHERE emo=%s"
        cursor.execute(wehave.format(gi=gid), (str(payload.emoji),))
        role_id = cursor.fetchall()
    except KeyError:
        # if the emoji isn't the one we care about then exit as well.
        return

    role = guild.get_role(role_id[0][1])
    if role is None:
        # make sure the role still exists and is valid.
        return
    # so we must get the member ourselves from the payload's `.user_id`.
    member = guild.get_member(payload.user_id)
    if member is None:
        # make sure the member still exists and is valid.
        return
    try:
        # Finally, remove the role.
        await member.remove_roles(role)
    except Exception as e:
        print(f"Ошибка: {str(e)}")

#welcome message
@bot.event
async def on_ready():
    print(f'Logged!')
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is None:
        # do things when they leave
        if len(before.channel.members) == 0:
            await asyncio.sleep(10)
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                except:
                    pass

#creating voice chat with yors param(name,limit users)
@bot.slash_command(description="create voice chat")
async def create(inter: disnake.ApplicationCommandInteraction,name='',count=0):
    try:
        print(name)
        if(name==''):
            channel2 = await inter.guild.create_voice_channel(name='xD')
        else:
            if(name ==0):
                channel2 = await inter.guild.create_voice_channel(name=name)
            else:
                channel2 = await inter.guild.create_voice_channel(name=name,user_limit=int(count))
        await inter.response.send_message('Sucessfully created', delete_after=10,ephemeral=True)
        await channel2.set_permissions(inter.author, mute_members = True, kick_members = True)
        await asyncio.sleep(10)
        if len(channel2.members) == 0:
            await channel2.delete()
    except:
        await inter.response.send_message('I couldn\'t do it', delete_after=10,ephemeral=True)
#@commands.has_any_role(здесь через запятую перечисляем роли)

#connecting members to databases
@bot.event
async def on_message(message):
    #local database for any guilds
    guild = str(message.guild.id)+'_emoji'
    create_table_role = """CREATE TABLE IF NOT EXISTS {table}(emo VARCHAR(100) PRIMARY KEY,rol BIGINT)"""
    cursor.execute(create_table_role.format(table=guild))
    cnn.commit()
    print(guild)
    create_table_rolem = """CREATE TABLE IF NOT EXISTS {table}(user_id BIGINT PRIMARY KEY,message_id BIGINT, role_id BIGINT)"""
    cursor.execute(create_table_rolem.format(table=guild+'_req'))
    cnn.commit()
    insert_emo = """INSERT IGNORE INTO {g} (emo,rol) VALUES (%s,%s)"""
    cursor.execute(insert_emo.format(g=guild), ('emo_msg',0,))
    cnn.commit()
    insert_emo = """INSERT IGNORE INTO {g} (emo,rol) VALUES (%s,%s)"""
    cursor.execute(insert_emo.format(g=guild), ('emo_msg_rl',0,))
    cnn.commit()
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)
    wehave = "SELECT * FROM discord_users WHERE id=(%s)"
    cursor.execute(wehave,(message.author.id,))
    result = cursor.fetchall()
    #register members score points
    if result == []:
        insert_movies_query = """INSERT INTO discord_users (id,money) VALUES ((%s),0)"""
        cursor.execute(insert_movies_query,(message.author.id,))
        cnn.commit()
        print("successfully inserted")
    wehave = "SELECT * FROM discord_users WHERE id=(%s)"
    cursor.execute(wehave,(message.author.id,))
    result = cursor.fetchall()
    print(f'Message: {message.content}')
#bot.add_cog(music_func.Music(bot))
bot.remove_command('help')
bot.run('your bot token')
