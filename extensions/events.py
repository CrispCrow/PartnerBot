"Bot events"

import hikari
import lightbulb

from db import Database
from utils import is_partner, parse_partnership_date

db = Database()
events = lightbulb.Plugin('Events')

@events.listener(hikari.GuildJoinEvent)
async def on_guild_join(event: hikari.GuildJoinEvent) -> None:
    await db.insert_guild_into_db(event.guild_id)


@events.listener(hikari.GuildLeaveEvent)
async def on_guild_join(event: hikari.GuildLeaveEvent) -> None:
    await db.delete_guild_from_db(event.guild_id)


@events.listener(hikari.MemberDeleteEvent)
async def on_member_leave(event: hikari.MemberDeleteEvent) -> None:
    if not await is_partner(event.guild_id, event.old_member.id):
        return

    notify_channel = await db.fetch_notify_channel(event.guild_id)
    partner = await db.fetch_partner(event.guild_id, event.old_member.id)
    partnership_date = await parse_partnership_date(partner['date'])
    await (await event.app.rest.fetch_channel(notify_channel)).send(
        hikari.Embed(
            title=f'Партнер {event.old_member} покинул сервер',
            color=0xFFB833
        )
        .add_field(name='📅 | Дата заключения', value=partnership_date)
        .add_field(name='🔗 | Ссылка на сервер', value=f'**[Вступить]({partner["url"]})**')
        .set_footer(text=f'Partner ID: {event.old_member.id}')
    )

    await db.delete_partner(event.guild_id, event.old_member.id)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(events)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(events)
