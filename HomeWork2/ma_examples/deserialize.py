from author import Author
from schema import AuthorSchema

json_data = """
    {
    "id": 1,
    "name": "Ivan",
    "email": "ivan@mail.ru"
    }
    """

schema = AuthorSchema()
result = schema.loads(json_data)
print(result)