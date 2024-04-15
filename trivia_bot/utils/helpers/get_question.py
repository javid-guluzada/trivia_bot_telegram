import json
import random
from trivia_bot.utils.helpers.question_model import Question

questions = []
with open("questions.json") as f:
    data = json.load(f)
    for item in data:
        question = Question.from_dict(item)
        questions.append(question)


def get_question_by_category(
    category_id: int, used_question_ids: list[int]
) -> Question | None:
    """
    Retrieves a question from the specified category that has not been used before.

    Args:
        category_id (int): The ID of the category to filter the questions.
        used_question_ids (list): A list of question IDs that have already been used.

    Returns:
        Question|None: A randomly selected question from the specified category that has not been used before.
        Returns None if no such question is found.
    """

    filtered_questions = [
        q
        for q in questions
        if q.category_id == category_id and q._id not in used_question_ids
    ]

    if filtered_questions != []:
        return random.choice(filtered_questions)
    else:
        return None
