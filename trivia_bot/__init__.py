import json

from logging import INFO, FileHandler, StreamHandler, basicConfig, getLogger
from os import getenv, remove, path
from dotenv import load_dotenv
from trivia_bot.utils.helpers.category_model import TriviaCategory

remove("log.txt")

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

log = getLogger("trivia_bot")

load_dotenv("config.env", override=True)

API_ID = getenv("API_ID")
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
OWNER_ID = int(getenv("OWNER_ID"))

if not all([API_ID, API_HASH, BOT_TOKEN, OWNER_ID]):
    log.error("Please fill in the config.env file")
    exit()

DATABASE_URI = getenv("DATABASE_URL")
DATABASE_NAME = getenv("DATABASE_NAME")
GROUPS_COLLECTION_NAME = getenv("GROUPS_COLLECTION_NAME")
USER_COLLECTION_NAME = getenv("USER_COLLECTION_NAME")

if not all([DATABASE_URI, DATABASE_NAME]):
    log.error("Please fill in the config.env file")
    exit()
else:
    from motor.motor_asyncio import AsyncIOMotorClient
    from umongo import Instance

    client = AsyncIOMotorClient(DATABASE_URI)
    db = client[DATABASE_NAME]
    instance = Instance.from_db(db)


with open("trivia_categories.json") as f:
    data = json.load(f)
    TRIVIA_CATEGORIES = [TriviaCategory.from_dict(category) for category in data]
