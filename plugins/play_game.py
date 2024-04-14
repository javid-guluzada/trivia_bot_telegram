from pyrogram import Client, filters
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)
from pyrogram.enums.chat_type import ChatType
import json
from utils.database.users_db import reset_user,update_category,update_score,update_question,get_game_status,get_question_ids,get_score,get_current_question_id
from utils.helpers.get_question import get_question_by_category

import random
import asyncio

with open("questions.json") as f:
    questions = json.load(f)

with open('trivia_categories.json') as f:
    trivia_categories = json.load(f)

@Client.on_message(filters.command("play_game"))
async def play_game(_, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        game_status= await get_game_status(message.from_user.id)
        if game_status:
            await message.reply_text("You already have an active game. Send /end_game to end it.")
        else:
            button_list = []
            for i in range(8):
                category_name = str(trivia_categories[i]['name'])
                category_id = str(trivia_categories[i]['id'])
                button_list.append([InlineKeyboardButton(category_name, callback_data=f"category_{category_id}")])

            button_list.append([InlineKeyboardButton("Next",callback_data="next_1")])
        
        await message.reply_text("Select a category to start the game.",reply_markup=InlineKeyboardMarkup(button_list))
    else:
        await message.reply_text("Please start a game in a private chat.")

@Client.on_callback_query(filters.regex(r"^next_") | filters.regex(r"prev_"))
async def next_category(_, callback: CallbackQuery):
    _, page = callback.data.split("_")
    page = int(page)
    button_list = []
    for i in range(8*page,8*(page+1)):
        button_list.append([InlineKeyboardButton(trivia_categories[i]['name'],callback_data=f"category_{trivia_categories[i]['id']}")])
    if page == 0:
        button_list.append([InlineKeyboardButton("Next",callback_data=f"next_1")])

    elif page == 2:
        button_list.append([InlineKeyboardButton("Previous",callback_data=f"prev_1")])

    else:
        button_list.append([InlineKeyboardButton("Previous",callback_data=f"prev_{page-1}"),InlineKeyboardButton("Next",callback_data=f"next_{page+1}")])
        
    await callback.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(button_list))


@Client.on_callback_query(filters.regex(r"^category_"))
async def category_selected(client:Client, callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    await update_category(callback.from_user.id,category_id)
    chat_id=callback.message.chat.id
    await callback.edit_message_text(f"Category selected successfully: {trivia_categories[category_id-9]['name']}")
    await send_question(client,category_id,chat_id)

@Client.on_callback_query(filters.regex(r"^option_"))
async def option_selected(client:Client, callback: CallbackQuery):
    option, correct_answer, category_id = callback.data.split("_")[1:]
    chat_id=callback.message.chat.id
    if option == correct_answer:
        await callback.edit_message_text("Correct answer!")
        await update_score(callback.from_user.id)
    else:
        await callback.edit_message_text(f"Wrong answer! The correct answer is {correct_answer}")
    await send_question(client,category_id,chat_id)   
    

async def send_question(client:Client,category_id:int,chat_id:int):
    question_ids = await get_question_ids(chat_id)
    question = get_question_by_category(category_id,question_ids)
    if question:
        await update_question(chat_id,question._id)
        options = question.incorrect_answers + [question.correct_answer]
        random.shuffle(options)
        button_list = []
        for option in options:
            button_list.append([InlineKeyboardButton(option,callback_data=f"option_{option}_{question.correct_answer}_{category_id}")])
        message=await client.send_message(chat_id,f"{question.question}\nSelect the correct answer. You have 1 minute",reply_markup=InlineKeyboardMarkup(button_list))
        await asyncio.sleep(60)
        current_question_id=await get_current_question_id(chat_id)  
        if current_question_id==question._id:
            score=await get_score(chat_id)
            await message.edit_text(f"Time's up! The correct answer is {question.correct_answer}\nGame over! Your final score is {score}.\nSend /play_game to start a new game.")
            await update_category(chat_id,0)
    else:
        await client.send_message(chat_id,"No questions available for this category. Please select another category.")
        await reset_user(chat_id)
