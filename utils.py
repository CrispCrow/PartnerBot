from __future__ import annotations
from typing import Optional
from datetime import datetime, timedelta

from db import Database

db = Database()

BASE_URL = 'https://discord.gg/'
INTERVALS = (
    ('месяцев', 2592000),
    ('недель', 604800),
    ('days', 86400),
    ('часов', 3600),
    ('минут', 60),
    ('секунд', 1)
)

async def is_partner(guild_id: int, partner_id: int) -> bool:
    """
    The function checks, that the partner exists into database
    
    :param guild_id: A guild id for search in database documents
    :param partner_id: A partner id for check exists
    :return: A bool value, that the partner exists into database or not
    """

    data = await db.fetch_document(guild_id)
    
    return True if str(partner_id) in data else False


async def gmt_time() -> datetime.datetime:
    """
    The function returns a date with format GMT+3
    
    :return: GMT+3 datetime.datetime object
    """

    return datetime.utcnow() + timedelta(hours=3)


async def parse_partnership_date(date: datetime.datetime) -> str:
    """
    The function is parsing provided date to human-readable format
    
    :param date: A date, that formatting is needed
    :return: Formatted string
    """

    parsed_date = date.strftime('%d.%m.%Yг., %H:%M:%S')
    days_partnership = display_time((await gmt_time()-date).total_seconds())

    return '{} ({} назад)'.format(parsed_date, days_partnership)


async def is_channel_into_db(guild_id: int, channel_id: int) -> bool:
    """
    The function checks, that channel field exists into database
    
    :param guild_id: A guild id for search in documents
    :param channel_id: A channel id for check existing
    :return: A bool value, is exists channel in database or not
    """

    try:
        partner_channel_id = await db.fetch_partner_channel(guild_id)
    except KeyError:
        return False

    return partner_channel_id == channel_id


async def is_notify_channel_into_db(guild_id: int, channel_id: int) -> bool:
    """
    The function checks, that channel field exists into database
    
    :param guild_id: A guild id for search in documents
    :param channel_id: A channel id for check existing
    :return: A bool value, is exists channel in database or not
    """

    try:
        partner_channel_id = await db.fetch_notify_channel(guild_id)
    except KeyError:
        return False

    return partner_channel_id == channel_id


async def check_context(query: str) -> Optional[dict[str, str]]:
    """
    The function checks, that a url is provided in certain text
    
    :param query: Text, that context checking is needed
    :return: A dict with partner text and url to discord server
    """

    words = query.split(' ')
    substring = list(filter(lambda element: BASE_URL in element, words))

    if not substring:
        return

    words.remove(substring[0])
    return dict(text=' '.join(words), url=substring[0])


def display_time(seconds: int) -> str: 
    """ 
    The function makes certain seconds
    to format months, weeks, days, hours...
  
    :param seconds: Seconds, that formatting is needed 
    :return: A string with formatted time
    """ 
  
    result = [] 
  
    for name, count in INTERVALS: 
        value = seconds // count 
        if value: 
            seconds -= value * count
            result.append("{} {}".format(int(value), name)) 
  
    return ', '.join(result[:2])