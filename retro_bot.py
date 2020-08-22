import discord
import inters
import random

client = discord.Client()
intlist = inters.Intlist('inters.json')

# https://discordapp.com/oauth2/authorize?&client_id=745978012692119642&scope=bot&permissions=8192
# // TODO
# 1. Add betting functionality
# 2. Add fighting scoreboard system
# 3. A !ditcher command that pings all the ditchers with their name so ppls who have role mentions surpressed still get pinged

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
    if message.content.startswith('!intlist'):
        # Make sure only Officers can use this command
        author_roles = [x.name for x in message.author.roles]
        if 'Officer' in author_roles or 'Meme Machine' in author_roles:
            # Get inters from our list
            inters = intlist.get_inters()
            # Sort them descending
            inters_sorted = sorted(inters, key=inters.get, reverse=True)
            # Post them in chat
            await message.channel.send(':star: Retro Top Inters :star:')
            count = 1
            for i in inters_sorted:
                await message.channel.send('{}. {}: {}'.format(count, i, inters[i]))
                count += 1

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

    # Fighting game
    if message.content.startswith('!fight'):
        # Fight initiator
        ini = message.author.id
        # Fight opponent
        opp = message.content.split(" ")[1]
        # Start message
        await message.channel.send(':crossed_swords: Fight between <@!{}> and {}! :crossed_swords:'.format(ini, opp))
        await message.channel.send('<@!{}><:peepobox:655086833029611522>       <:peepobox2:655088598646784019>:{}'.format(ini, opp))
        # Get latest message id, so we can edit it
        async for msg in message.channel.history(limit=1):
                latest_msg = msg
        # Animation 1
        await latest_msg.edit(content='<@!{}> <:peepobox:655086833029611522>     <:peepobox2:655088598646784019> {}'.format(ini, opp))
        # Animation 2
        await latest_msg.edit(content='<@!{}>  <:peepobox:655086833029611522>   <:peepobox2:655088598646784019>  {}'.format(ini, opp))
        # Animation 3
        await latest_msg.edit(content='<@!{}>   <:peepobox:655086833029611522>:boom:<:peepobox2:655088598646784019>   {}'.format(ini, opp))
        # Decide win by coin flip
        if random.randint(0,1) == 0:
            # Initiator wins
            await latest_msg.edit(content='<@!{}>   <:peepobox:655086833029611522> :skull_crossbones:   {}'.format(ini, opp))
            await message.channel.send('<@!{}> has won the fight!'.format(ini))
        else:
            # Opponent wins
            await latest_msg.edit(content='<@!{}>   :skull_crossbones: <:peepobox2:655088598646784019>   {}'.format(ini, opp))
            await message.channel.send('{} has won the fight!'.format(opp))

client.run('NzQ1OTc4MDEyNjkyMTE5NjQy.Xz5oKQ.3Rk1syY51PZ3dvlXOksYwE8XGuY')