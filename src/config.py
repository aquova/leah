import discord, json

CONFIG_PATH = "/private/config.json"
with open(CONFIG_PATH) as config_file:
    cfg = json.load(config_file)

DISCORD_KEY = cfg['discord']
ART_CHANS = cfg['channels']['listening']
VERIFY_CHAN = cfg['channels']['verify']
GALLERY_CHAN = cfg['channels']['gallery']

intents = discord.Intents.default()
client = discord.Client(intents=intents)
