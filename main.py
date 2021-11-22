from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext

bot = Client(intents=Intents.default())
slash = SlashCommand(bot)

@slash.slash(name="link")
async def link(ctx: SlashContext):
    # TODO stuff
