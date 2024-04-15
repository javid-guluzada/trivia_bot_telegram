from typing import List


class Question:
    """
    Represents a trivia question.

    Attributes:
        _id (int): The unique identifier of the question.
        category_id (int): The unique identifier of the category the question belongs to.
        type (str): The type of the question (e.g., "multiple" or "boolean").
        difficulty (str): The difficulty level of the question (e.g., "easy", "medium", or "hard").
        category (str): The category of the question.
        question (str): The text of the question.
        correct_answer (str): The correct answer to the question.
        incorrect_answers (List[str]): A list of incorrect answers to the question.

    """

    id: int
    category_id: int
    type: str
    difficulty: str
    category: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]

    def __init__(
        self,
        _id: int,
        category_id: int,
        type: str,
        difficulty: str,
        category: str,
        question: str,
        correct_answer: str,
        incorrect_answers: List[str],
    ):
        self._id = _id
        self.category_id = category_id
        self.type = type
        self.difficulty = difficulty
        self.category = category
        self.question = question
        self.correct_answer = correct_answer
        self.incorrect_answers = incorrect_answers

    @staticmethod
    def from_dict(data: dict) -> "Question":
        """
        Creates a Question object from a dictionary.

        Args:
            data (dict): A dictionary containing the question data.

        Returns:
            Question: A Question object created from the dictionary.
        """
        return Question(
            data["_id"],
            data["category_id"],
            data["type"],
            data["difficulty"],
            data["category"],
            data["question"],
            data["correct_answer"],
            data["incorrect_answers"],
        )
