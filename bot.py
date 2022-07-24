"Bot module"

import os
import logging

import dotenv

import hikari
import lightbulb

dotenv.load_dotenv()

log = logging.getLogger()

bot = lightbulb.BotApp(
    prefix='p!',
    token=os.environ.get('BOT_TOKEN'),
    case_insensitive_prefix_commands=True,
    owner_ids=tuple, # owner IDs
    intents=hikari.Intents.ALL
)
bot.load_extensions_from('./extensions')

@bot.listen(hikari.StartingEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    log.info('Bot started.')


def run() -> None:
    bot.run(
        activity=hikari.Activity(
            name='p!help',
            type=hikari.ActivityType.WATCHING
        )
    )
