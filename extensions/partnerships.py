"Partnership commands"

import hikari
import lightbulb

from db import Database
from utils import (
    is_partner,
    parse_partnership_date,
    is_channel_into_db,
    is_notify_channel_into_db,
    check_context
)

db = Database()
partner = lightbulb.Plugin('PartnerShips')

@partner.command
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.guild_only)
@lightbulb.option('text', 'Текст партнерства', modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.option('partner', 'Партнер для добавления', type=hikari.Member)
@lightbulb.command('добавить', 'Добавить партнера в список партнеров', pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def add_partner(
    ctx: lightbulb.PrefixContext,
    partner: hikari.User,
    text: str,
) -> None:
    context = await check_context(text)
    if await is_partner(ctx.guild_id, partner.id):
        await ctx.respond(
            hikari.Embed(
                title='Добавление партнера',
                description='Данный участник уже является партнером сервера',
                color=0xFF3933
            )
        )
        return
    if not context:
        await ctx.respond(
            hikari.Embed(
                title='Установка текста партнера',
                description='В полученном тексте не было найдено ссылки на сервер',
                color=0xFF3933
            )
        )
        return

    await db.add_partner(ctx.guild_id, partner.id, context['text'], context['url'])
    partner_channel = await db.fetch_partner_channel(ctx.guild_id)

    await ctx.respond(
        hikari.Embed(
            title='Вы добавили нового партнера',
            description=f'Текст партнера {partner.mention} был отправлен в <#{partner_channel}>',
            color=0xFFB833
        )
    )

    await (await ctx.app.rest.fetch_channel(partner_channel)).send(
        hikari.Embed(
            title='Новое партнерство',
            description=context['text'],
            color=0xFFB833
        )
        .add_field(name='🔗 | Ссылка на сервер', value=f'**[Вступить]({context["url"]})**')
        .add_field(name='🤵 | Партнер', value=partner)
        .set_footer(text=f'Partner ID: {partner.id}')
    )


@partner.command
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.guild_only)
@lightbulb.option('partner', 'Партнер для удаления', type=hikari.Member)
@lightbulb.command('удалить', 'Удалить партнера из списка партнеров', pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def remove_partner(
    ctx: lightbulb.PrefixContext,
    partner: hikari.Member
) -> None:
    if not await is_partner(ctx.guild_id, partner.id):
        await ctx.respond(
            hikari.Embed(
                title='Удаление партнера',
                description='Данный участник не является партнером сервера',
                color=0xFF3933
            )
        )
        return

    await db.delete_partner(ctx.guild_id, partner.id)
    await ctx.respond(
        hikari.Embed(
            title='Партнер удален',
            description=f'Участник {partner.mention} больше не партнер этого сервера',
            color=0xFFB833
        )
    )


@partner.command
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.guild_only)
@lightbulb.option('partner', 'Партнер сервера', type=hikari.Member)
@lightbulb.command('партнер', 'Информация о партнере', pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def info_partner(
    ctx: lightbulb.PrefixContext,
    partner: hikari.Member
) -> None:
    if not await is_partner(ctx.guild_id, partner.id):
        await ctx.respond(
            hikari.Embed(
                title='Информация о партнере',
                description='Данный участник не является партнером сервера',
                color=0xFF3933
            )
        )
        return

    partner_data = await db.fetch_partner(ctx.guild_id, partner.id)
    partnership_date = await parse_partnership_date(partner_data['date'])
    await ctx.respond(
        hikari.Embed(
            title=f'Информация о партнере {partner}',
            description=partner_data['text'],
            color=0xFFB833
        )
        .add_field(name='📅 | Дата заключения', value=partnership_date)
        .add_field(name='🔗 | Ссылка на сервер', value=f'**[Вступить]({partner_data["url"]})**')
        .set_footer(text=f'Partner ID: {partner.id}')
    )


@partner.command
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.guild_only)
@lightbulb.option('channel', 'Канал партнерств', type=hikari.TextableGuildChannel)
@lightbulb.command('канал', 'Установить канал партнерств', pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def channel_partner(
    ctx: lightbulb.PrefixContext,
    channel: hikari.TextableGuildChannel
) -> None:
    if await is_channel_into_db(ctx.guild_id, channel.id):
        await ctx.respond(
            hikari.Embed(
                title='Канал партнерств',
                description='Данный канал уже установлен для партнерств',
                color=0xFF3933
            )
        )
        return

    await db.set_partner_channel(ctx.guild_id, channel.id)
    await ctx.respond(
        hikari.Embed(
            title='Канал партнерств установлен',
            description=f'Все текста партнеров будут отправляться в {channel.mention}',
            color=0xFFB833
        )
    )


@partner.command
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.guild_only)
@lightbulb.option('channel', 'Канал уведомлений', type=hikari.TextableGuildChannel)
@lightbulb.command('уведомления', 'Установить канал уведомлений', pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def notify_channel(
    ctx: lightbulb.PrefixContext,
    channel: hikari.TextableGuildChannel
) -> None:
    if await is_notify_channel_into_db(ctx.guild_id, channel.id):
        await ctx.respond(
            hikari.Embed(
                title='Канал уведомлений',
                description='Данный канал уже установлен для уведомлений',
                color=0xFF3933
            )
        )
        return

    await db.set_notify_channel(ctx.guild_id, channel.id)
    await ctx.respond(
        hikari.Embed(
            title='Канал уведомлений установлен',
            description=f'Все уведомления будут отправляться в {channel.mention}',
            color=0xFFB833
        )
    )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(partner)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(partner)
