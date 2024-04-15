from pymongo.errors import DuplicateKeyError
from trivia_bot import USER_COLLECTION_NAME, instance
from umongo import Document, fields
import logging

logger = logging.getLogger(__name__)


@instance.register
class User(Document):
    user_id = fields.IntField(attribute="_id")
    is_game_active = fields.BooleanField(default=False)
    score = fields.IntField(default=0)
    category_id = fields.IntField(default=0)
    current_question_id = fields.IntField(default=0)
    questions_used = fields.ListField(fields.IntField(), default=[])

    class Meta:
        collection_name = USER_COLLECTION_NAME


async def add_user(user_id: int) -> User:
    """
    Adds a new user to the database.

    Args:
        user_id (int): The ID of the user to add to the database.

    Returns:
        User: The user that was added to the database.
    """
    try:
        user = User(
            user_id=user_id,
            is_game_active=False,
            score=0,
            category_id=0,
            current_question_id=0,
            questions_used=[],
        )
        return await user.commit()
    except DuplicateKeyError:
        logger.info(f"User {user_id} already exists in the database.")


async def get_user(user_id: int) -> User:
    """
    Retrieves a user from the database.

    Args:
        user_id (int): The ID of the user to retrieve from the database.

    Returns:
        User: The user with the specified ID.
    """
    user = await User.find_one({"_id": user_id})
    if not user:
        user = await add_user(user_id)
    return user


async def get_game_status(user_id: int) -> bool:
    """
    Retrieves the game status of a user.

    Args:
        user_id (int): The ID of the user to retrieve the game status for.

    Returns:
        bool: The game status of the user.
    """
    user = await get_user(user_id)
    return user.is_game_active


async def get_question_ids(user_id: int) -> list:
    """
    Retrieves the question IDs for a user.

    Args:
        user_id (int): The ID of the user to retrieve the question IDs for.

    Returns:
        list: The question IDs for the user.
    """
    user = await get_user(user_id)
    return list(user.questions_used)


async def get_score(user_id: int) -> int:
    """
    Retrieves the score of a user.

    Args:
        user_id (int): The ID of the user to retrieve the score for.

    Returns:
        int: The score of the user.
    """
    user = await get_user(user_id)
    return user.score


async def get_current_question_id(user_id: int) -> int:
    """
    Retrieves the current question ID for a user.

    Args:
        user_id (int): The ID of the user to retrieve the current question ID for.

    Returns:
        int: The current question ID for the user.
    """
    user = await get_user(user_id)
    return user.current_question_id


async def set_game_status(user_id: int, status: bool):
    """
    Sets the game status of a user.

    Args:
        user_id (int): The ID of the user to set the game status for.
        status (bool): The game status to set.
    """
    user = await get_user(user_id)
    user.is_game_active = status
    await user.commit()


async def reset_user(user_id: int):
    """
    Resets a user's game state.

    Args:
        user_id (int): The ID of the user to reset.
    """
    user = await get_user(user_id)
    user.is_game_active = False
    user.score = 0
    user.category_id = 0
    user.current_question_id = 0
    user.questions_used = []
    await user.commit()


async def update_question(user_id: int, question_id: int):
    """
    Updates the current question for a user.

    Args:
        user_id (int): The ID of the user to update.
        question_id (int): The ID of the new question.
    """
    user = await get_user(user_id)
    user.current_question_id = question_id
    user.questions_used.append(question_id)
    await user.commit()


async def update_score(user_id: int):
    """
    Updates a user's score.

    Args:
        user_id (int): The ID of the user to update.
    """
    user = await get_user(user_id)
    user.score += 1
    await user.commit()


async def update_category(user_id: int, category_id: int):
    """
    Updates a user's selected category.

    Args:
        user_id (int): The ID of the user to update.
        category_id (int): The ID of the new category.
    """
    user = await get_user(user_id)
    user.category_id = category_id
