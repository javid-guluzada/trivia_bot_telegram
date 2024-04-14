import json
from logging import INFO, FileHandler, StreamHandler, basicConfig, getLogger
from os import getenv,remove,path
from pyrogram import Client, __version__, enums
from pyrogram.raw.all import layer
from dotenv import load_dotenv

#if path.exists('log.txt'):
#    remove('log.txt')

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[FileHandler('log.txt'), StreamHandler()],
            level=INFO)

LOGGER = getLogger(__name__)

load_dotenv('config.env',override=True)

API_ID = getenv('API_ID')
API_HASH = getenv('API_HASH')
BOT_TOKEN = getenv('BOT_TOKEN')
OWNER_ID= int(getenv('OWNER_ID'))

if not all([API_ID, API_HASH, BOT_TOKEN, OWNER_ID]):
    LOGGER.error('Please fill in the config.env file')
    exit()

DATABASE_URI = getenv('DATABASE_URL')
DATABASE_NAME = getenv('DATABASE_NAME')
GROUPS_COLLECTION_NAME = getenv('GROUPS_COLLECTION_NAME')
USER_COLLECTION_NAME = getenv('USER_COLLECTION_NAME')

if not all([DATABASE_URI, DATABASE_NAME]):
    LOGGER.error('Please fill in the config.env file')
    exit()
else:
    from motor.motor_asyncio import AsyncIOMotorClient
    from umongo import Instance
    client = AsyncIOMotorClient(DATABASE_URI)
    db = client[DATABASE_NAME]
    instance = Instance.from_db(db)



class Bot(Client):
    """
    A subclass of pyrogram. Client representing the Trivia Bot.

    Attributes:
        name (str): The name of the bot.
    """

    def __init__(self):
        """
        Initializes the Bot object.

        Sets up the bot with the necessary API credentials and configurations.
        """
        name = "trivia_bot"
        super().__init__(
            name,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root=f"plugins"),
            parse_mode=enums.ParseMode.HTML,
        )

    async def start(self):
        """
        Starts the bot.

        Connects to the Telegram API and logs the bot's username and Pyrogram version.
        """
        await super().start()
        me=await self.get_me()
        LOGGER.info(
            f"@{me.username}  started. Pyrogram v{__version__} (Layer {layer})"
        )

    async def stop(self, *args):
        """
        Stops the bot.

        Disconnects from the Telegram API and logs a message indicating that the bot has stopped.
        """
        await super().stop()
        LOGGER.info("Bot stopped. Bye.")

if __name__ == '__main__':
    bot = Bot()
    bot.run()
