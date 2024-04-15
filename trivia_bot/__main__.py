from pyrogram import Client, enums, __version__

from logging import getLogger

from trivia_bot import API_ID, API_HASH, BOT_TOKEN


log = getLogger("trivia_bot")


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
            plugins=dict(root=f"{name}/plugins"),
            parse_mode=enums.ParseMode.HTML,
        )

    async def start(self):
        """
        Starts the bot.

        Connects to the Telegram API and logs the bot's username and Pyrogram version.
        """
        await super().start()
        me = await self.get_me()
        log.info(f"@{me.username}  started. Pyrogram v{__version__}")

    async def stop(self, *args):
        """
        Stops the bot.

        Disconnects from the Telegram API and logs a message indicating that the bot has stopped.
        """
        await super().stop()
        log.info("Bot stopped. Bye.")


bot = Bot()
bot.run()
