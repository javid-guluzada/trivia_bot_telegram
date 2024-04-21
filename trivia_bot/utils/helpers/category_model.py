class TriviaCategory:
    """
    Represents a trivia category.

    Attributes:
        id (int): The ID of the category.
        name (str): The name of the category.
    """

    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    @staticmethod
    def from_dict(data: dict) -> "TriviaCategory":
        """
        Creates a TriviaCategory object from a dictionary.

        Args:
            data (dict): The dictionary containing the category data.

        Returns:
            TriviaCategory: The created TriviaCategory object.
        """
        return TriviaCategory(data["id"], data["name"])
