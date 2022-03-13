# Leah
# Written by aquova et al., 2022
# https://github.com/aquova/leah

import discord
from config import client, DISCORD_KEY,\
    ART_CHANS, MOD_CHANS, VERIFY_CHAN, GALLERY_CHAN, SHOWCASE_CHAN,\
    SHOWCASE_ROLES
from typing import Optional

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
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    # Ignore messages that have been handled previously
    if reaction.message.id in leah.posted:
        return

    # Staff reactions to verification channel posts by this client
    if reaction.message.channel.id == VERIFY_CHAN:
        # Ignore reactions to posts not by this client in verification channel
        if client.user != reaction.message.author:
            return

        # Publish verified posts to gallery channel
        await publish_art(message=reaction.message)

    # User reactions to posts in self-curated channel
    elif reaction.message.channel.id in MOD_CHANS:
        # Ignore reactions from users other than the message author
        if user != reaction.message.author:
            return

        # Ignore reactions from users without any of the required roles
        if len(SHOWCASE_ROLES) == 0 or len([r for r in user.roles if r.id in SHOWCASE_ROLES]) == 0:
            return

        # Publish self-curated posts
        await reaction.message.add_reaction(emoji=reaction.emoji)
        await publish_mod(message=reaction.message, reaction=reaction)

    # User reactions to posts in showcase channel
    elif reaction.message.channel.id == SHOWCASE_CHAN:
        # Ignore reactions from users other than the message author
        if user != await get_original_author(reaction.message):
            return

        # Remove bulletin posts
        await reaction.message.delete()

@client.event
async def on_message(message: discord.Message):
    # Ignore all bots
    if message.author.bot:
        return

    # Send posts from creative channel to verification channel
    if message.channel.id in ART_CHANS:
        await verify_art(message=message)

async def verify_art(message: discord.Message):
    verify = client.get_channel(id=VERIFY_CHAN)
    for img in message.attachments:
        await verify.send(f"<@{message.author.id}> has posted:\n{message.content}\n{img.url}")

async def publish_art(message: discord.Message):
    gallery = client.get_channel(id=GALLERY_CHAN)
    user = message.mentions[0]
    title = f"Some amazing art by {user}"
    split = message.content.split('\n')
    text = split[-2]
    embed = discord.Embed(title=title, type="rich", color=user.color, description=text)
    embed.set_image(url=split[-1])
    await send_embed(channel=gallery, embed=embed, message=message)

async def publish_mod(message: discord.Message, reaction: discord.Reaction):
    channel = client.get_channel(id=SHOWCASE_CHAN)
    user = message.author
    title = f"{reaction.emoji} posted in #{str(message.channel)}"
    text = f"{message.content}"
    embed = discord.Embed(title=title, description=text, type="rich", color=user.color)

    # Include original embedded content
    url = None
    if len(message.embeds) > 0:
        e = message.embeds[0]
        url = e.image.proxy_url
        if url is discord.embeds.EmptyEmbed:
            url = e.thumbnail.proxy_url
    else:
        if len(message.attachments) > 0:
            url = message.attachments[0].url
    if url is not None and url is not discord.embeds.EmptyEmbed:
        embed.set_image(url=url)

    # Fill in embed info with original message context
    embed.url = message.jump_url
    embed.set_author(name=user.display_name, url=embed.url, icon_url=user.avatar_url)

    await send_embed(channel=channel, embed=embed, message=message)

async def send_embed(channel: discord.TextChannel, embed: discord.Embed, message: discord.Message):
    leah.posted.add(message.id)
    await channel.send(embed=embed)

async def get_original_author(showcase_message: discord.Message) -> Optional[discord.Member]:
    split_url = showcase_message.embeds[0].url.split('/')
    original_channel = showcase_message.guild.get_channel(int(split_url[-2]))
    try:
        original_message = await original_channel.fetch_message(int(split_url[-1]))
        return original_message.author
    except discord.DiscordException:
        return None

client.run(DISCORD_KEY)
