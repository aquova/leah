# Leah
# main.py
# Written by aquova et al., 2022
# https://github.com/StardewValleyDiscord/leah

import random
import strings
import discord
from discord.ext import commands
from config import COMMAND_PREFIX, EXTENSIONS, GUILDS, DISCORD_KEY, DISCORD_INTENTS, \
    ART_CHANS, MOD_CHANS, VERIFY_CHAN, GALLERY_CHAN, SHOWCASE_CHAN, VERIFY_ROLES, SHOWCASE_ROLES
from typing import Optional
from utils import check_roles, format_roles_error


# Bot definition
class Leah(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=DISCORD_INTENTS,
            description=strings.get("client_description"),
            allowed_mentions=discord.AllowedMentions.none())
        self.posted = set()

    async def sync_guild(self, guild: discord.Guild):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def setup_hook(self) -> None:
        # Load all extensions on setup
        for ext in EXTENSIONS:
            await self.load_extension(name=ext)

    async def on_ready(self):
        print(strings.get("client_login").format(bot.user.name, bot.user.discriminator, bot.user.id))


bot = Leah()


@bot.listen(name="on_message")
async def on_message(message: discord.Message) -> None:
    """
    For messages in listening channels, reposts a preview to the verification channel.
    """
    # Ignore all bots
    if message.author.bot:
        return

    # Send posts from listening channels to verification channel
    if message.channel.id in ART_CHANS:
        await verify_art(message=message)

@bot.tree.context_menu(name="Publish", guilds=GUILDS)
async def command_publish(interaction: discord.Interaction, message: discord.Message):
    """
    Reposts a message from a self-curated or verification channel as a formatted embed to a showcase or gallery channel,
    respectively, depending on the channel the original message was posted in.
    Posts in showcase channels may also be removed with this command.
    """
    reply = None
    success = False      # Reactions are added to messages based on success or failure
    fail_quietly = True  # Failure reactions are hidden by default

    # Staff interactions on verification channel posts by this bot
    if message.channel.id == VERIFY_CHAN:

        # Verification errors are shown to all to avoid repeat attempts
        fail_quietly = False

        # Ignore interactions from users without any of the required roles
        if not check_roles(interaction.user, VERIFY_ROLES):
            reply = format_roles_error(VERIFY_ROLES)

        # Ignore messages that have been handled previously
        elif message.id in bot.posted:
            reply = strings.get("publish_error_posted")

        # Ignore reactions to invalid posts or posts not by this client in verification channel
        elif bot.user != message.author or not await publish_art(message=message):
            reply = strings.get("publish_error_user")

        # Publish verified posts to gallery channel
        else:
            reply = strings.get("publish_response_verified").format(f"<#{GALLERY_CHAN}>")
            success = True

    # User interactions on posts in self-curated channel
    elif message.channel.id in MOD_CHANS:

        # Ignore interactions from users without any of the required roles
        if not check_roles(interaction.user, SHOWCASE_ROLES):
            reply = format_roles_error(SHOWCASE_ROLES)

        # Ignore interactions from users other than the message author
        elif interaction.user != message.author or not isinstance(interaction.user, discord.Member):
            reply = strings.get("publish_error_curated_other")

        # Ignore messages that have been handled previously
        elif message.id in bot.posted:
            reply = strings.get("publish_error_posted")

        # Publish self-curated posts
        else:
            reply = strings.get("publish_response_curated_self").format(f"<#{SHOWCASE_CHAN}>")
            success = True
            await publish_mod(message=message)

    # User interactions on posts in showcase channel
    elif message.channel.id == SHOWCASE_CHAN:

        # Users without a showcase role may still remove any of their posts from the showcase

        # Ignore interactions from users other than the message author
        if interaction.user != await get_original_author(message):
            reply = strings.get("publish_error_remove_other")

        # Remove showcase posts
        else:
            reply = strings.get("publish_response_remove_self")
            success = True
            await message.delete()

    # User interactions on posts in unhandled channels
    else:
        reply = strings.get("publish_error_channel")

    # Send a secret reply to the commander
    if reply is None:
        reply = strings.get("publish_error_generic")
    await interaction.response.send_message(reply, ephemeral=True)

    # Add a reaction to the post to show it's been interacted with
    try:
        if success or not fail_quietly:
            await message.add_reaction(strings.emoji_success if success else strings.emoji_failure)
    except:
        return

async def verify_art(message: discord.Message) -> None:
    """
    Creates a formatted message preview of a message for the bot to send in the verification channel.
    :param message: The original message from a listening channel.
    """
    verify = bot.get_channel(VERIFY_CHAN)
    for img in message.attachments:
        await verify.send(strings.get("message_verify").format(f"<@{message.author.id}>", message.content, img.url))

async def publish_art(message: discord.Message) -> bool:
    """
    Creates a published message with embedded content for the bot to report in the gallery channel.
    """
    gallery = bot.get_channel(GALLERY_CHAN)
    try:
        member = await message.guild.fetch_member(message.raw_mentions[0])
        title = random.choice(strings.get("message_gallery")).format(member)
        split = message.content.split('\n')
        text = split[-2]
        embed = discord.Embed(title=title, type="rich", color=member.color, description=text)
        embed.set_image(url=split[-1])
        await send_embed(channel=gallery, embed=embed, message=message)
    except:
        return False
    return True

async def publish_mod(message: discord.Message) -> None:
    """
    Creates a published message with embedded content for the bot to repost in the showcase channel.
    """
    channel = bot.get_channel(SHOWCASE_CHAN)
    user = message.author
    title = strings.get("message_showcase").format(str(message.channel))
    text = message.content
    embed = discord.Embed(title=title, description=text, type="rich", color=user.color)

    # Include original embedded content
    url = None
    if len(message.embeds) > 0:
        e = message.embeds[0]
        url = e.image.proxy_url
        if url is None:
            url = e.thumbnail.proxy_url
    else:
        if len(message.attachments) > 0:
            url = message.attachments[0].url
    if url is not None:
        embed.set_image(url=url)

    # Fill in embed info with original message context
    embed.url = message.jump_url
    embed.set_author(name=user.display_name, url=embed.url, icon_url=user.display_avatar.url)

    await send_embed(channel=channel, embed=embed, message=message)

async def send_embed(channel: discord.TextChannel, embed: discord.Embed, message: discord.Message) -> None:
    """
    Record a message as posted and then send to the given channel.
    :param channel: The channel in which to send the embed.
    :param embed: A formatted embed based on some user-created message.
    :param message: The original message from a listening or self-curated channel.
    """
    bot.posted.add(message.id)
    await channel.send(embed=embed)

async def get_original_author(showcase_message: discord.Message) -> Optional[discord.Member]:
    """
    Showcase messages are bot-reposts of other user-created messages.

    We can fetch the user who authored the original message by following the jumplink from the repost.
    :param showcase_message: A message posted in any showcase channel.
    :return: The original author of a given self-curated showcase message, or None if not found.
    """
    # We store a jumplink to the original message in the embed URL, as created in publish_mod()
    split_url = showcase_message.embeds[0].url.split('/')
    original_channel = showcase_message.guild.get_channel(int(split_url[-2]))
    try:
        original_message = await original_channel.fetch_message(int(split_url[-1]))
        return original_message.author
    except discord.DiscordException:
        return None


# Run the bot with configured intents
bot.run(DISCORD_KEY)
