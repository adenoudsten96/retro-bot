import os
import random
import discord
import inters
import re
import datetime

from sqlalchemy import create_engine, Column, String, Integer, or_, and_, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

############################# DB ######################################
engine = create_engine('sqlite:///bot.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Fight(Base):
    __tablename__ = 'fights'

    id       = Column(Integer, primary_key=True)
    user     = Column(String)
    opponent = Column(String)
    winner   = Column(String)

    def __init__(self, user, opponent, winner):
        self.user = user
        self.opponent = opponent
        self.winner = winner

class Game(Base):
    __tablename__ = 'games'

    id   = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

class GamePlayers(Base):
    __tablename__ = 'game_players'

    id        = Column(Integer)
    game_id   = Column(Integer, primary_key=True)
    player_id = Column(Integer, primary_key=True)

    def __init__(self, game_id, player_id):
        self.game_id = game_id
        self.player_id = player_id

class Event(Base):
    __tablename__ = 'events'

    id             = Column(Integer, primary_key=True)
    discord_msg_id = Column(Integer)
    game           = Column(Integer)
    created_by     = Column(Integer)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, discord_msg_id, game, created_by):
        self.discord_msg_id = discord_msg_id
        self.game = game
        self.created_by = created_by

Base.metadata.create_all(engine)
############################# DB ######################################

########################### GLOBAL ##################################
accepted = "<:accepted:759402101398175784>"
declined = "<:declined:759402093227409418>"
tentative = "<:tentative:759402084633804842>"
client = discord.Client()
intlist = inters.Intlist('inters.json')
# https://discordapp.com/oauth2/authorize?&client_id=745978012692119642&scope=bot&permissions=8192

## counters ##
accepted_counter = 0 
declined_counter = 0
tentative_counter = 0
########################### GLOBAL ##################################

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
    
    # LFM system
    if message.content.startswith("!lfm"):

        # Get game name
        try:
            game = message.content.split('"')[1]
        except:
            await message.channel.send(":robot: Something went wrong. Did you put the game name in quotes?")
            return
        # Get time
        when = message.content.split('"')[2:]
        if not when:
            when = "Sometime tonight"

        # Save event to DB
        sess = Session()
        new_event = Event(discord_msg_id=message.id, game=game.lower(), created_by=message.author.id)
        sess.add(new_event)
        sess.commit()
        
        ###### Embed construct ########

        # Add group members as tentative
        try:
            game_id = sess.query(Game).filter(Game.name == game.lower()).one()
        except:
            await message.channel.send(":robot: Game not found. Use !addgame")
            return
        gamers = sess.query(GamePlayers).filter(GamePlayers.game_id == game_id.id).all()
        global tentative_counter
        tentative_counter = len(gamers)
        tent = ""
        for gamer in gamers:
            tent += "<@!{}>\n".format(gamer.player_id)
        sess.close()

        colours = [0x1cde12, 0x25bab8, 0x4f1db3, 0xc9163a]

        embedVar = discord.Embed(title="**{} wants to play {}!**".format(message.author.display_name, game), color=random.choice(colours))
        embedVar.add_field(name=":clock8: Time", value="{}".format(when[0]), inline=False)
        embedVar.add_field(name="{} Accepted (0)".format(accepted), value="{}".format("-"), inline=True)
        embedVar.add_field(name="{} Declined (0)".format(declined), value="{}".format("-"), inline=True)
        embedVar.add_field(name="{} Tentative ({})".format(tentative, tentative_counter), value="{}".format(tent), inline=True)
        embedVar.set_footer(text='Created by {} on {} \nUse the buttons below to join/leave. Creator can ping/DM all gamers in group.'.format(message.author.name, datetime.date.today().strftime("%d/%m")))
        x = await message.channel.send(embed=embedVar)
        ###### Embed construct ########

        # Add emoji to message
        await x.add_reaction(accepted)
        await x.add_reaction(declined)
        await x.add_reaction(tentative)
        await x.add_reaction("🗑️")
        await x.add_reaction("❗")
        await x.add_reaction("✉️")

    # Add gamers to game
    if message.content.split(" ")[0] == "!addgamers":
        # Get the game, save as lowercase
        try:
            game = message.content.split('"')[1].lower()
        except:
            await message.channel.send(":robot: Something went wrong")
            return

        # Get the gamers to be added to the game, normalize ID's
        try:
            gamers = message.content.split('"')[2].split(" ")[1:]
        except:
            await message.channel.send(":robot: Something went wrong")
            return

        # Add gamers to game
        counter = 0
        sess = Session()
        for gamer in gamers:
            gamer = re.sub("\ |\@|\&|\!|\<|\>", '', gamer)
            # Check if gamer already exists
            gamer_exists = sess.query(GamePlayers).filter(GamePlayers.player_id == int(gamer)).count()
            if gamer_exists:
                await message.channel.send(":robot: <@!{}> already in group for game {}, skipping..".format(gamer, game.capitalize()))
            else:
                # Add gamer to game
                game_id = sess.query(Game).filter(Game.name == game).one()
                new_gamer = GamePlayers(game_id.id, gamer)
                sess.add(new_gamer)
                counter += 1
        sess.commit()
        sess.close()
        await message.channel.send(":robot: Added {} gamers to group {}".format(counter, game.capitalize()))

    # Remove gamers from game
    if message.content.split(" ")[0] == "!removegamers":
        # Get the game, save as lowercase
        try:
            game = message.content.split('"')[1].lower()
        except:
            await message.channel.send(":robot: Something went wrong")
            return

        # Get the gamers to be removed from the game, normalize ID's
        try:
            gamers = message.content.split('"')[2].split(" ")[1:]
        except:
            await message.channel.send(":robot: Something went wrong")
            return

        # Remove gamers to game
        counter = 0
        sess = Session()
        for gamer in gamers:
            gamer = re.sub("\ |\@|\&|\!|\<|\>", '', gamer)
            # Check if gamer exists
            gamer_exists = sess.query(GamePlayers).filter(GamePlayers.player_id == int(gamer)).count()
            if gamer_exists:
                sess.query(GamePlayers).filter(GamePlayers.player_id == int(gamer)).delete()
                counter += 1
            else:
                await message.channel.send(":robot: <@!{}> not in group for game {}, skipping..".format(gamer, game.capitalize()))
        sess.commit()
        sess.close()
        await message.channel.send(":robot: Removed {} gamers from group {}".format(counter, game.capitalize()))

    # Add game
    if message.content.split(" ")[0] == "!addgame":
        # Get the game, save as lowercase
        try:
            game = message.content.split('"')[1].lower()
        except:
            await message.channel.send(":robot: Could not add game. Did you put the game name in quotes?")
            return

        # Add game to game database if not exists
        sess = Session()
        game_exists = sess.query(Game).filter(Game.name == game).count()
        if not game_exists:
            new_game = Game(game)
            sess.add(new_game)
            sess.commit()
            sess.close()
            await message.channel.send(":robot: Game added")
        else:
            await message.channel.send(":robot: Game already exists")
            return


@client.event
async def on_reaction_add(reaction, user):

    def process_choice(reaction, user, index):
        '''
        Updates the list of accepted, declined or tentative users based on which list is passed in with index.
        '''

        # Get counters
        global accepted_counter
        global declined_counter
        global tentative_counter

        # Get users from lists
        acc_list = reaction.message.embeds[0].fields[1].value.split("\n")
        dec_list = reaction.message.embeds[0].fields[2].value.split("\n")
        tent_list = reaction.message.embeds[0].fields[3].value.split("\n")

        def remove_user(l):
            '''
            This function removes the user from a list, and turns it back into a string to pass to the embed.
            '''
            for i in l:
                if i == "<@!{}>".format(user.id) or i == "<@{}>".format(user.id):
                    l.remove(i)
            if l == []:
                new_list = "-"
                return new_list
            new_list = ""
            for i in l:
                new_list += "{}\n".format(i)
            return new_list

        def update_counters():
            '''
            This function updates the global counters by checking the length of each list.
            '''
            global accepted_counter
            global declined_counter
            global tentative_counter

            accepted_counter = len(acc_list)
            declined_counter = len(dec_list)
            tentative_counter = len(tent_list)

        # Remove user from all lists and decrement counters
        if index == 4:
            new_dec = remove_user(dec_list)
            new_tent = remove_user(tent_list)
            new_acc = remove_user(acc_list)
            update_counters()
            updated_embed = reaction.message.embeds[0].set_field_at(1, name="{} Accepted ({})".format(accepted, accepted_counter), value=new_acc)
            updated_embed = reaction.message.embeds[0].set_field_at(2, name="{} Declined ({})".format(declined, declined_counter), value=new_dec)
            updated_embed = reaction.message.embeds[0].set_field_at(3, name="{} Tentative ({})".format(tentative, tentative_counter), value=new_tent)
            return updated_embed

        # Return if already in list
        current_accepted = reaction.message.embeds[0].fields[index].value.split("\n")
        for i in current_accepted:
            if i == "<@{}>".format(user.id):
                return 0
        
        # Add user to list and update the counters
        updated_list = reaction.message.embeds[0].fields[index].value.strip("-")
        updated_list += "\n{}".format(user.mention)
        update_counters()

        # Update and return the new embed based on index
        if index == 1:
            new_dec = remove_user(dec_list)
            new_tent = remove_user(tent_list)
            update_counters()
            updated_embed = reaction.message.embeds[0].set_field_at(1, name="{} Accepted ({})".format(accepted, accepted_counter), value=updated_list)
            updated_embed = reaction.message.embeds[0].set_field_at(2, name="{} Declined ({})".format(declined, declined_counter), value=new_dec)
            updated_embed = reaction.message.embeds[0].set_field_at(3, name="{} Tentative ({})".format(tentative, tentative_counter), value=new_tent)
            return updated_embed
        elif index == 2:
            new_acc = remove_user(acc_list)
            new_tent = remove_user(tent_list)
            update_counters()
            updated_embed = reaction.message.embeds[0].set_field_at(1, name="{} Accepted ({})".format(accepted, accepted_counter), value=new_acc)
            updated_embed = reaction.message.embeds[0].set_field_at(2, name="{} Declined ({})".format(declined, declined_counter), value=updated_list)
            updated_embed = reaction.message.embeds[0].set_field_at(3, name="{} Tentative ({})".format(tentative, tentative_counter), value=new_tent)
            return updated_embed
        elif index == 3:
            new_acc = remove_user(acc_list)
            new_dec = remove_user(dec_list)
            update_counters()
            updated_embed = reaction.message.embeds[0].set_field_at(1, name="{} Accepted ({})".format(accepted, accepted_counter), value=new_acc)
            updated_embed = reaction.message.embeds[0].set_field_at(2, name="{} Declined ({})".format(declined, declined_counter), value=new_dec)
            updated_embed = reaction.message.embeds[0].set_field_at(3, name="{} Tentative ({})".format(tentative, tentative_counter), value=updated_list)
            return updated_embed

    if user == client.user:
        return

    # Check if reaction was added to embed, which is usually an Event
    if reaction.message.embeds:

        # Accept - index 1
        if str(reaction) == accepted:
            new_embed = process_choice(reaction, user, 1)
            if new_embed == 0:
                return
            await reaction.message.edit(embed=new_embed)
            await reaction.message.remove_reaction(accepted, user)

        # Decline - index 2
        if str(reaction) == declined:
            new_embed = process_choice(reaction, user, 2)
            if new_embed == 0:
                return
            await reaction.message.edit(embed=new_embed)
            await reaction.message.remove_reaction(declined, user)

        # Tentative - index 3
        if str(reaction) == tentative:
            new_embed = process_choice(reaction, user, 3)
            if new_embed == 0:
                return
            await reaction.message.edit(embed=new_embed)
            await reaction.message.remove_reaction(tentative, user)

        # Remove
        if str(reaction) == "🗑️":
            new_embed = process_choice(reaction, user, 4)
            if new_embed == 0:
                return
            await reaction.message.edit(embed=new_embed)
            await reaction.message.remove_reaction("🗑️", user)

        # Ping
        if str(reaction) == "❗":
            await reaction.message.remove_reaction("❗", user)

        # DM
        if str(reaction) == "✉️":
            await reaction.message.remove_reaction("✉️", user)

client.run(os.environ['RETROBOT'])


# Might need this later
# async def my_background_task():
#     await client.wait_until_ready()
#     while not client.is_closed():
#         message = await client.get_channel(channelId).fetch_message(messageId)
#         await message.edit(embed = newEmbed)
#         await asyncio.sleep(300)

# bg_task = client.loop.create_task(my_background_task())