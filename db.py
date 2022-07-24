"Database module"

import os

import hikari
from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    def __init__(self) -> None:
        self.cluster = AsyncIOMotorClient(os.getenv('MONGODB_CONNECTION'))
        self.db = self.cluster['partnerbot']['partners']

    async def add_partner(
        self,
        guild_id: int,
        partner_id: int,
        partner_text: str,
        partner_url: str
    ) -> None:
        """
        The method adds certain user into database
        
        :param guild_id: Guild id for insert field _id into document
        :param partner_id: User, that adding into database
        :param partner_text: User's text
        :partner_url: User's url to discord server
        """

        from utils import gmt_time # circular import

        await self.db.update_one(
            {'_id': guild_id},
            {
            '$set': {
                str(partner_id): {
                    'date': await gmt_time(),
                    'text': partner_text,
                    'url': partner_url
                    }
                }
            }
        )

    async def fetch_partner_channel(self, guild_id: int) -> int:
        """
        The method search a partner channel into db
        
        :param guild_id: Guild id for searching document
        :return: Guild id
        """

        return (await self.db.find_one({'_id': guild_id}))['partner_channel']

    async def set_partner_channel(self, guild_id: int, channel_id: int) -> None:
        """
        The method sets partner channel for guild
        
        :param guild_id: Guild id for searching document
        :param channel_id: Channel id for adding field into document
        """

        await self.db.update_one(
            {'_id': guild_id}, {'$set': {'partner_channel': channel_id}}
        )

    async def insert_guild_into_db(self, guild_id: int) -> None:
        """
        The method inserts guild to database
        
        :param guild_id: Guild to insert
        """
        await self.db.insert_one({'_id': guild_id})

    async def delete_guild_from_db(self, guild_id: int) -> None:
        """
        The method removes guild from database
        
        :param guild_id: Guild to remove
        """

        await self.db.delete_one({'_id': guild_id})

    async def delete_partner(self, guild_id: int, partner_id: int) -> None:
        """
        The method removes partner from database
        
        :param guild_id: Guild id for searching document
        :param partner_id: Partner to remove
        """

        await self.db.update_one({'_id': guild_id}, {'$unset': {str(partner_id): ''}})

    async def fetch_document(self, guild_id: int) -> dict:
        """
        The method fetch document with certain parameter into database
        
        :param guild_id: Guild id for searching
        :return: Dict object with document data
        """

        return (await self.db.find_one({'_id': guild_id}))

    async def fetch_partner(self, guild_id: int, partner_id: int) -> dict:
        """
        The method fetch partner into database
        
        :param guild_id: Guild id for searching document
        :param partner_id: Partner to search
        :return: Dict object with partner data
        """

        return (await self.db.find_one({'_id': guild_id}))[str(partner_id)]

    async def fetch_notify_channel(self, guild_id: int) -> int:
        """
        The method fetch notify channel into database
        
        :param guild_id: Guild for searching
        :return: Notification channel id
        """

        return (await self.db.find_one({'_id': guild_id}))['notify_channel']

    async def set_notify_channel(self, guild_id: int, channel_id: int) -> None:
        """
        The method set notification channel field into document
        
        :param guild_id: Guild id for searching document
        :param channel_id: Channel to set
        """

        await self.db.update_one(
            {'_id': guild_id}, {'$set': {'notify_channel': channel_id}}
        )