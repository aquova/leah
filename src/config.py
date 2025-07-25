# Leah
# config.py
# Written by aquova et al., 2022
# https://github.com/StardewValleyDiscord/leah

import discord
import yaml

# Read config file
CONFIG_PATH = "private/config.yaml"
with open(CONFIG_PATH) as config_file:
    cfg = yaml.safe_load(config_file)

# Parse config file
DISCORD_INTENTS: discord.Intents = discord.Intents(
    guilds=True,
    guild_messages=True,
    message_content=True,
    emojis=True
)
DISCORD_KEY = cfg["discord"]
ART_CHANS = cfg["channels"]["listening"]
MOD_CHANS = cfg["channels"]["selfcurated"]
VERIFY_CHAN = cfg["channels"]["verify"]
GALLERY_CHAN = cfg["channels"]["gallery"]
SHOWCASE_CHAN = cfg["channels"]["showcase"]
ROLES_CHAN = cfg["channels"]["roles"]
ADMIN_ROLE = cfg["roles"]["admin"]
VERIFY_ROLES = cfg["roles"]["verify"]
SHOWCASE_ROLES = cfg["roles"]["showcase"]
EXTENSIONS = cfg["extensions"]
ALLOW_SHOWCASE_OTHER_USERS = cfg["options"]["allow_showcase_other_users"]
COMMAND_PREFIX = cfg["command_prefix"]
