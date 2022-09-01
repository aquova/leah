import discord, json

CONFIG_PATH = "/private/config.json"
with open(CONFIG_PATH) as config_file:
    cfg = json.load(config_file)

DISCORD_KEY = cfg['discord']
ART_CHANS = cfg['channels']['listening']
MOD_CHANS = cfg['channels']['selfcurated']
VERIFY_CHAN = cfg['channels']['verify']
GALLERY_CHAN = cfg['channels']['gallery']
SHOWCASE_CHAN = cfg['channels']['showcase']
SHOWCASE_ROLES = cfg['roles']['showcase']

intents: discord.Intents = discord.Intents(**{flag: True for flag in cfg["intents"]})
client = discord.Client(intents=intents)
