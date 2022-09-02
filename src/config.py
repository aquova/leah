# Leah
# config.py
# Written by aquova et al., 2022
# https://github.com/StardewValleyDiscord/leah

import discord, json

# Read config file
CONFIG_PATH = "./private/config.json"
with open(CONFIG_PATH) as config_file:
    cfg = json.load(config_file)

# Parse config file
DISCORD_INTENTS: discord.Intents = discord.Intents(**{flag: True for flag in cfg["intents"]})
DISCORD_KEY = cfg["discord"]
ART_CHANS = cfg["channels"]["listening"]
MOD_CHANS = cfg["channels"]["selfcurated"]
VERIFY_CHAN = cfg["channels"]["verify"]
GALLERY_CHAN = cfg["channels"]["gallery"]
SHOWCASE_CHAN = cfg["channels"]["showcase"]
ROLES_CHAN = cfg["channels"]["roles"]
ADMIN_ROLES = cfg["roles"]["admin"]
VERIFY_ROLES = cfg["roles"]["verify"]
SHOWCASE_ROLES = cfg["roles"]["showcase"]
EXTENSIONS = cfg["extensions"]
COMMAND_PREFIX = cfg["command_prefix"]
GUILDS = [discord.Object(id=guild_id) for guild_id in cfg["guilds"]]
