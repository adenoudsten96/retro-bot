import os
import random
import discord
import inters
import re

from sqlalchemy import create_engine, Column, String, Integer, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

## DB ##
engine = create_engine('sqlite:///bot.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Fight(Base):
    __tablename__ = 'fights'

    id = Column(Integer, primary_key=True)
    user = Column(String)
    opponent = Column(String)
    winner = Column(String)

    def __init__(self, user, opponent, winner):
        self.user = user
        self.opponent = opponent
        self.winner = winner

Base.metadata.create_all(engine)
## DB ##

client = discord.Client()
intlist = inters.Intlist('inters.json')
# https://discordapp.com/oauth2/authorize?&client_id=745978012692119642&scope=bot&permissions=8192

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # Ignore our own messages
    if message.author == client.user:
        return
    
    # Nuke X amount of messages
    if message.content.startswith('!nuke'):
        # Make sure only Officers can use this command
        author_roles = [x.name for x in message.author.roles]
        if 'Officer' in author_roles:
            try:
                # Get the amount of messages that need to be wiped
                amount = int(message.content.split(" ")[1])
            except:
                # Ignore Index out of Range exceptions
                pass
            # Delete the messages
            async for msg in message.channel.history(limit=(amount + 1)):
                await msg.delete()
        else:
            pass
    
    # Show all inters
    if message.content == '!intlist':
        author_roles = [x.name for x in message.author.roles]
        if 'Raider' in author_roles:
            # Get inters from our list
            inters = intlist.get_inters()
            # Sort them descending
            inters_sorted = sorted(inters, key=inters.get, reverse=True)
            # Post them in chat
            await message.channel.send(':star: Retro Top Inters :star:')
            count = 1
            rankings = ""
            for i in inters_sorted:
                rankings += '{}. {}: {} \n'.format(count, i, inters[i])
                count += 1
            await message.channel.send(rankings)

    # Add one int to specified user
    if message.content.startswith('!int'):
        author_roles = [x.name for x in message.author.roles]
        if 'Officer' in author_roles:
            try:
                # Get the person who needs to be added to the int list and add them
                name = message.content.split(" ")[1]
                intlist.add_int(name)
                await message.channel.send(':robot: :point_right: Added 1 int to {}'.format(name))
            except:
                pass

    # Clear int list
    if message.content == '!intreset':
        author_roles = [x.name for x in message.author.roles]
        if 'Officer' in author_roles:
            try:
                intlist.reset()
                await message.channel.send(':robot: Done boss')
            except:
                pass
    
    # Link seth youtube video
    if message.content == '!seth':
        await message.channel.send('<:kekw:620973601214169116> https://www.youtube.com/watch?v=2ILRYT8Mc80')

    # Link agane youtube video
    if message.content == '!agane':
        await message.channel.send('<:agane:702877283001565254> https://www.youtube.com/watch?v=YlKkX38NgGo')

    # Fighting history
    if message.content == "!fighthistory":
        peepobox = "<:peepobox:655086833029611522>"
        peepobox2 = "<:peepobox2:655088598646784019>"
        sess = Session()
        user = message.author.id
        wins = sess.query(Fight).filter(or_(Fight.user == user, Fight.opponent == user), and_(Fight.winner == user)).count()
        losses = sess.query(Fight).filter(or_(Fight.user == user, Fight.opponent == user), and_(Fight.winner != user)).count()
        win_percentage = ( wins / (wins + losses) * 100)
        # # Check if user has a recorded fight history before continuing
        # if wins == 0 or losses == 0:
        #     await message.channel.send("No fighting history for <@!{}>. Get to fighting! {}".format(message.author.id, peepobox2))
        #     return
        
        latest_fights_query = sess.query(Fight).filter(or_(Fight.user == user, Fight.opponent == user)).order_by(Fight.id.desc()).limit(3).all()
        sess.close()

        latest_fights = ""
        for i in latest_fights_query:
            if i.winner == str(message.author.id):
                # Win
                if i.opponent == str(message.author.id):
                    latest_fights += ":crown: **Win** against <@!{}> \n".format(i.user)
                else:
                    latest_fights += ":crown: **Win** against <@!{}> \n".format(i.opponent)
            else:
                # Loss
                latest_fights += ":skull_crossbones: **Loss** against <@!{}> \n".format(i.winner)

        embedVar = discord.Embed(title="{} Fight history for {} {}".format(peepobox, message.author.display_name, peepobox2), color=0xeb4034)
        embedVar.add_field(name=":crown: Wins", value="{}".format(wins), inline=True)
        embedVar.add_field(name=":skull_crossbones: Losses", value="{}".format(losses), inline=True)
        embedVar.add_field(name=":trophy: Win percentage", value="{}%".format(round(win_percentage)), inline=True)
        embedVar.add_field(name="Latest results", value=latest_fights, inline=False)
        embedVar.set_thumbnail(url='https://www.iconfinder.com/data/icons/essentials-volume-3/128/boxing-gloves-512.png')
        
        await message.channel.send(embed=embedVar)

    # Fighting game
    if message.content.startswith('!fight'):
        # Fight initiator
        ini = message.author.id

        # Normalize ID's from different sources using regex
        try:
            opp = message.content.split(" ")[1]
            opp = re.sub("\ |\@|\&|\!|\<|\>", '', opp)
        except Exception as e:
            return

        # Don't allow fighting yourself
        if str(ini) == opp:
            await message.channel.send("Stop fighting yourself <:pepega:591965438666342413>")
            return
        # Start message
        await message.channel.send(':crossed_swords: Fight between <@!{}> and <@!{}>! :crossed_swords:'.format(ini, opp))
        await message.channel.send('<@!{}><:peepobox:655086833029611522>       <:peepobox2:655088598646784019>:<@!{}>'.format(ini, opp))
        # Get latest message id, so we can edit it
        async for msg in message.channel.history(limit=1):
                latest_msg = msg
        # Animation 1
        await latest_msg.edit(content='<@!{}> <:peepobox:655086833029611522>     <:peepobox2:655088598646784019> <@!{}>'.format(ini, opp))
        # Animation 2
        await latest_msg.edit(content='<@!{}>  <:peepobox:655086833029611522>   <:peepobox2:655088598646784019>  <@!{}>'.format(ini, opp))
        # Animation 3
        await latest_msg.edit(content='<@!{}>   <:peepobox:655086833029611522>:boom:<:peepobox2:655088598646784019>   <@!{}>'.format(ini, opp))
        
        # Set up DB connection
        sess = Session()

        # Decide win by coin flip
        if random.randint(0,1) == 0:
            # Initiator wins
            winner = Fight(ini, opp, ini)
            sess.add(winner)
            sess.commit()
            sess.close()
            await latest_msg.edit(content='<@!{}>   <:peepobox:655086833029611522> :skull_crossbones:   <@!{}>'.format(ini, opp))
            await message.channel.send('<@!{}> has won the fight!'.format(ini))
        else:
            # Opponent wins
            winner = Fight(ini, opp, opp)
            sess.add(winner)
            sess.commit()
            sess.close()
            await latest_msg.edit(content='<@!{}>   :skull_crossbones: <:peepobox2:655088598646784019>   <@!{}>'.format(ini, opp))
            await message.channel.send('<@!{}>  has won the fight!'.format(opp))

    # Fighting champion
    if message.content.startswith('!champion'):

        # Get win count for each user
        scores = {}
        sess = Session()
        all_users = sess.execute("""select distinct user from
                                (select distinct user as user from fights UNION
                                select distinct opponent as user from fights)
                                """)
        for user in all_users:
            wins = sess.query(Fight).filter(Fight.winner == user[0]).count()
            scores[str(user[0])] = wins
        
        # Determine user with highest score
        scores_sorted = sorted(scores, key=scores.get, reverse=True)
        champion = ":trophy: <@!{}> has won {} fights and is the fighting champion! :trophy:".format(scores_sorted[0],scores[scores_sorted[0]])
        await message.channel.send(champion)
    
    # LFG system
    if message.content.startswith("!lfg"):
        game = message.content.split('"')[1]
        when = message.content.split('"')[2]
        if not when:
            when = "Sometime tonight"
        embedVar = discord.Embed(title="**{} wants to play {}!**".format(message.author.name, game), color=0x427ef5)
        embedVar.add_field(name=":point_right: Current gamers:", value="{} <@!745978012692119642>".format(message.author.mention), inline=True)
        embedVar.add_field(name=":alarm_clock: When:", value="{}".format(when), inline=True)
        embedVar.add_field(name="Join voice:", value="[click](https://discordapp.com/746773831183761428/752602234121879572)".format(when), inline=False)
        embedVar.set_footer(text='Use the reactions below to join or to ping/DM all gamers in group (only creator).')
        embedVar.set_thumbnail(url='https://static.wikia.nocookie.net/be327120-a2dd-4467-bf86-8c2212037668')
        x = await message.channel.send(embed=embedVar)
        await x.add_reaction("➕")
        await x.add_reaction("➖")
        await x.add_reaction("❗")
        await x.add_reaction("✉️")


# @client.event
# async def on_reaction_add(reaction, user):

#     if user == client.user:
#         return
    
#     print('reaction added by', user.name)
#     print(reaction)
#     print(user)
#     print(reaction.message)
#     await reaction.message.channel.send("<@!85098921382125568> <@!745978012692119642>")


client.run(os.environ['RETROBOT'])
