# Leah
# main.py
# Written by aquova et al., 2022
# https://github.com/StardewValleyDiscord/leah

import random
import strings
import discord
from discord.ext import commands
from config import COMMAND_PREFIX, EXTENSIONS, DISCORD_KEY, DISCORD_INTENTS, \
    ART_CHANS, MOD_CHANS, VERIFY_CHAN, GALLERY_CHAN, SHOWCASE_CHAN, VERIFY_ROLES, SHOWCASE_ROLES, ADMIN_ROLE
from importlib import reload
from typing import Optional
from utils import check_roles, format_roles_error


# Bot definition
class Leah(commands.Bot):
    """
    Bot used for curating and publishing submissions in Discord channels for a given guild.
    Includes methods for updating and reloading commands and strings during runtime.
    """
    def __init__(self):
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=DISCORD_INTENTS,
            description=strings.get("client_description"),
            allowed_mentions=discord.AllowedMentions.none())

    async def setup_hook(self):
        """
        Inherited from Client. Called once internally after login. Used to load all initial command extensions.
        """
        # Load all extensions on setup
        for ext in EXTENSIONS:
            await self.load_extension(name=ext)

    async def on_ready(self):
        """
        Inherited from Client. Called once internally after all setup. Used only to log notice.
        """
        print(strings.get("client_login").format(bot.user.name, bot.user.discriminator, bot.user.id))

    async def sync_guild(self, guild: discord.Guild):
        """
        Syncs app commands from this bot with the remote Discord state when required to apply changes.
        :param guild: Discord guild to sync commands with.
        """
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    def reload_strings(self) -> None:
        """
        Reloads all text strings from data file for bot commands and interactions.
        """
        reload(strings)


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

@bot.tree.context_menu(name=strings.get("app_name_publish"), guilds=[guild.id for guild in bot.guilds])
async def command_publish(interaction: discord.Interaction, message: discord.Message):
    """
    Reposts a message from a self-curated or verification channel as a formatted embed to a showcase or gallery channel,
    respectively, depending on the channel the original message was posted in.
    Posts in showcase channels may also be removed with this command.
    """
    reply = None
    success = False      # Reactions are added to messages based on success or failure
    fail_quietly = True  # Failure reactions are hidden by default

    # We avoid duplicate publish actions by checking for reactions
    posted = False
    for reaction in message.reactions:
        posted = bot.user in [user async for user in reaction.users()]
        if posted:
            break

    # Interactions on verification channel posts by this bot
    if message.channel.id == VERIFY_CHAN:

        # Verification errors are shown to all to avoid repeat attempts
        fail_quietly = False

        # Ignore interactions from users without any of the required roles
        if not check_roles(interaction.user, VERIFY_ROLES):
            reply = format_roles_error(strings.get("commands_error_roles"), VERIFY_ROLES)

        # Ignore messages that have been handled previously
        elif posted:
            reply = strings.get("publish_error_posted")
            fail_quietly = True

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
            reply = format_roles_error(strings.get("commands_error_roles"), SHOWCASE_ROLES)

        # Ignore interactions from users other than the message author
        elif interaction.user != message.author:
            reply = strings.get("publish_error_curated_other")

        # Ignore messages that have been handled previously
        elif posted:
            reply = strings.get("publish_error_posted")
            fail_quietly = True

        # Publish self-curated posts
        else:
            reply = strings.get("publish_response_curated_self").format(f"<#{SHOWCASE_CHAN}>")
            success = True
            await publish_mod(message=message)

    # User interactions on posts in showcase channel
    elif message.channel.id == SHOWCASE_CHAN:

        # Skip the usual role check when trying to remove posts
        # Users without a showcase role may still remove any of their posts from the showcase
        linked_message = await get_linked_message(repost_message=message)

        # Ignore interactions from users other than the message author
        if interaction.user != linked_message.author:
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
    emoji = strings.emoji_success if success else strings.emoji_failure
    if reply is None:
        reply = strings.get("publish_error_generic")
    await interaction.response.send_message(f"{emoji}\t{reply}\n{message.jump_url}", ephemeral=True)

    # Add a reaction to the post to show it's been interacted with
    if message is not None and (success or not fail_quietly):
        await message.add_reaction(emoji)

async def verify_art(message: discord.Message) -> None:
    """
    Creates a formatted message preview of a message for the bot to send in the verification channel.
    :param message: The original message from a listening channel.
    """
    verify = bot.get_channel(VERIFY_CHAN)
    for img in message.attachments:
        await verify.send(strings.get("message_verify").format(f"<@{message.author.id}>", message.content, img.url, message.jump_url))

async def publish_art(message: discord.Message) -> bool:
    """
    Creates a published message with embedded content for the bot to repost in the gallery channel.
    """
    gallery = bot.get_channel(GALLERY_CHAN)
    author = await message.guild.fetch_member(message.raw_mentions[0])
    linked_message = await get_linked_message(repost_message=message)
    if linked_message is None:
        return False
    title = random.choice(strings.get("message_gallery")).format(str(linked_message.channel))
    split = message.content.split("\n")
    # Add original text content
    text = "\n".join(split[1:-2])
    embed = discord.Embed(title=title, description=text, type="rich", colour=author.colour)
    # Add original embedded content
    embed.set_image(url=split[-1])
    # Add jumplink to original message
    embed.url = split[-2]
    # Add user preview
    embed.set_author(name=author.display_name, url=embed.url, icon_url=author.display_avatar.url)
    await send_embed(channel=gallery, embed=embed, message=message)
    return True

async def publish_mod(message: discord.Message) -> None:
    """
    Creates a published message with embedded content for the bot to repost in the showcase channel.
    """
    channel = bot.get_channel(SHOWCASE_CHAN)
    author = await message.guild.fetch_member(message.author.id)
    source_embed = None
    # Check for linked content
    url = None
    if len(message.embeds) > 0:
        source_embed = message.embeds[0]
        url = source_embed.image.proxy_url
        if url is None:
            url = source_embed.thumbnail.proxy_url
    else:
        if len(message.attachments) > 0:
            url = message.attachments[0].url
    title = strings.get("message_showcase").format(str(message.channel)) if source_embed is None else source_embed.title
    # Add original text content
    text = message.content if source_embed is None or message.content != source_embed.url else f"{source_embed.url}\n\n{source_embed.description}"
    embed = discord.Embed(title=title, description=text, type="rich", colour=author.colour)
    # Add original embedded content
    if url is not None:
        embed.set_image(url=url)
    # Add jumplink to original message
    embed.url = message.jump_url
    # Add user preview
    embed.set_author(name=author.display_name, url=embed.url, icon_url=author.display_avatar.url)
    await send_embed(channel=channel, embed=embed, message=message)

async def send_embed(channel: discord.TextChannel, embed: discord.Embed, message: discord.Message) -> None:
    """
    Send an embed to the given channel and do any extra actions.
    :param channel: The channel in which to send the embed.
    :param embed: A formatted embed based on some user-created message.
    :param message: The original message from a listening or self-curated channel.
    """
    # We don't do anything else here currently :/
    await channel.send(embed=embed)

async def get_linked_message(repost_message: discord.Message) -> Optional[discord.Message]:
    """
    Showcase messages are bot-reposts of other user-created messages.

    We can fetch the user who authored the original message by following the jumplink from the repost.
    :param repost_message: A message posted in any showcase channel.
    :return: The original author of a given self-curated showcase message, or None if not found.
    """
    # A jumplink to the original message in the embed URL for us to parse here
    url = repost_message.content.split("\n")[-2] if repost_message.channel.id == VERIFY_CHAN else repost_message.embeds[0].url
    split_url = url.split("/")
    original_channel = repost_message.guild.get_channel(int(split_url[-2]))
    original_message = None if original_channel is None else await original_channel.fetch_message(int(split_url[-1]))
    return original_message


# Run the bot with configured intents
bot.run(DISCORD_KEY)
