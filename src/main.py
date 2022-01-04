# Leah
# Written by aquova, 2022
# https://github.com/aquova/leah

import discord
from config import client, DISCORD_KEY, ART_CHANS, VERIFY_CHAN, GALLERY_CHAN

class Leah:
    def __init__(self):
        self.posted = set()

leah = Leah()

@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.id != VERIFY_CHAN or client.user != reaction.message.author:
        return
    if reaction.message.id in leah.posted:
        return
    leah.posted.add(reaction.message.id)
    txt = reaction.message.content.split('\n')
    other = reaction.message.mentions[0]
    embed = discord.Embed(title=f"Some amazing art by {str(other)}", type="rich", color=other.color, description=txt[-2])
    embed.set_image(url=txt[-1])
    gallery = client.get_channel(GALLERY_CHAN)
    await gallery.send(embed=embed)

@client.event
async def on_message(message):
    # Ignore all bots
    if message.author.bot:
        return

    if message.channel.id in ART_CHANS:
        verify = client.get_channel(VERIFY_CHAN)
        for img in message.attachments:
            await verify.send(f"<@{message.author.id}> has posted:\n{message.content}\n{img.url}")

client.run(DISCORD_KEY)
