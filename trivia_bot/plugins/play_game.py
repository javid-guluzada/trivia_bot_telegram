import random
import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram.enums.chat_type import ChatType

from trivia_bot import TRIVIA_CATEGORIES, OWNER_ID
from trivia_bot.utils.database import users_db
from trivia_bot.utils.helpers.get_question import get_question_by_category

log = logging.getLogger(__name__)


@Client.on_message(filters.command("play_game"))
async def play_game(_, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        game_status = await users_db.get_game_status(message.from_user.id)
        if game_status:
            await message.reply_text(
                "You already have an active game. Send /end_game to end it."
            )
        else:
            await users_db.set_game_status(message.from_user.id, True)
            button_list = []
            for i in range(8):
                button_list.append(
                    [
                        InlineKeyboardButton(
                            TRIVIA_CATEGORIES[i].name,
                            callback_data=f"category_{TRIVIA_CATEGORIES[i].id}",
                        )
                    ]
                )

            button_list.append([InlineKeyboardButton("Next", callback_data="next_1")])

            new_message = await message.reply_text(
                "Select a category to start the game.",
                reply_markup=InlineKeyboardMarkup(button_list),
            )
            await users_db.update_message_id(message.from_user.id, new_message.id)
    else:
        await message.reply_text("Please start a game in a private chat.")


@Client.on_callback_query(filters.regex(r"^next_") | filters.regex(r"prev_"))
async def next_category(_, callback: CallbackQuery):
    _, page = callback.data.split("_")
    page = int(page)
    button_list = []
    for i in range(8 * page, 8 * (page + 1)):
        button_list.append(
            [
                InlineKeyboardButton(
                    TRIVIA_CATEGORIES[i].name,
                    callback_data=f"category_{TRIVIA_CATEGORIES[i].id}",
                )
            ]
        )
    if page == 0:
        button_list.append([InlineKeyboardButton("Next", callback_data=f"next_1")])

    elif page == 2:
        button_list.append([InlineKeyboardButton("Previous", callback_data=f"prev_1")])

    else:
        button_list.append(
            [
                InlineKeyboardButton("Previous", callback_data=f"prev_{page-1}"),
                InlineKeyboardButton("Next", callback_data=f"next_{page+1}"),
            ]
        )

    await callback.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(button_list)
    )


@Client.on_callback_query(filters.regex(r"^category_"))
async def category_selected(client: Client, callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    await users_db.update_category(callback.from_user.id, category_id)
    chat_id = callback.message.chat.id
    category_name = next(
        (category.name for category in TRIVIA_CATEGORIES if category.id == category_id),
        None,
    )
    text = f"Category selected successfully: {category_name}"
    await callback.edit_message_text(text)

    await send_question(client, callback, category_id, chat_id, text)


@Client.on_callback_query(filters.regex(r"^option_"))
async def option_selected(client: Client, callback: CallbackQuery):
    option, correct_answer, category_id = callback.data.split("_")[1:]
    chat_id = callback.message.chat.id
    text = ""
    if option == correct_answer:
        text = "Correct answer!"
        await users_db.update_score(callback.from_user.id, True)
    else:
        text = f"Wrong answer! The correct answer is {correct_answer}"
        await users_db.update_score(callback.from_user.id, False)
    await callback.edit_message_text(text)
    await send_question(client, callback, int(category_id), chat_id, text)


async def send_question(
    client: Client,
    callback: CallbackQuery,
    category_id: int,
    chat_id: int,
    old_text: str,
):
    question_ids = await users_db.get_question_ids(chat_id)
    question = get_question_by_category(category_id, question_ids)
    if question:
        try:
            button_list = []
            await users_db.update_question(chat_id, question._id)

            if question.type == "boolean":
                options = ["True", "False"]
            else:
                options = question.incorrect_answers + [question.correct_answer]
                random.shuffle(options)

            for option in options:
                button_list.append(
                    [
                        InlineKeyboardButton(
                            option,
                            callback_data=f"option_{option}_{question.correct_answer}_{category_id}",
                        )
                    ]
                )
            await callback.edit_message_text(
                f"{old_text}\n{question.question}\nSelect the correct answer. You have 1 minute",
                reply_markup=InlineKeyboardMarkup(button_list),
            )
            await asyncio.sleep(60)
            current_question_id = await users_db.get_current_question_id(chat_id)
            if current_question_id == question._id:
                correct_answers, wrong_answers = await users_db.get_score(chat_id)
                await callback.edit_message_text(
                    f"Time's up! The correct answer is {question.correct_answer}\nGame over! Your final score is \nCorrect answers - {correct_answers} \nWrong answers - {wrong_answers}.\nSend /play_game to start a new game."
                )
                await users_db.reset_user(chat_id)
        except Exception as e:
            log.error(e)
            log.error(f"Question: {question}")
            await client.send_message(
                OWNER_ID,
                f"An error occurred while sending question to {chat_id}. Error: {e}",
            )
            await asyncio.sleep(1)
            await client.send_message(OWNER_ID, f"Question: {question.to_dict()}")
            await asyncio.sleep(1)
            game_status = await users_db.get_game_status(chat_id)
            if game_status:
                await send_question(client, callback, category_id, chat_id, old_text)
    else:
        await callback.edit_message_text(
            chat_id,
            "No questions available for this category. Please select another category.",
        )
        await users_db.reset_user(chat_id)


@Client.on_message(filters.command("end_game") & filters.private)
async def end_game(client: Client, message: Message):
    game_status = await users_db.get_game_status(message.from_user.id)
    if game_status:
        message_id = await users_db.get_message_id(message.from_user.id)
        await client.delete_messages(message.chat.id, message_id)
        await users_db.reset_user(message.from_user.id)
        await message.reply_text("Game ended successfully.")
    else:
        await message.reply_text("You don't have an active game.")
