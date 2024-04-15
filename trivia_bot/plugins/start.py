from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "Hello! I am a Trivia Bot. Send /play_game to start a new game."
    )
