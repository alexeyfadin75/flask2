from api import ma
from api.models.quote import QuoteModel
from api.schemas.author import AuthorSchema


def rating_validate(value:int):
    """ Функция возвращает проверку допустимого диапазона rating"""
    # Если  rating в допустимом диапазоне то возвращается True
    return value in range (1,6)


class QuoteSchema(ma.SQLAlchemySchema):
    class Meta:
        model = QuoteModel


    id = ma.auto_field()
    text = ma.auto_field()
    author = ma.Nested(AuthorSchema(only=("name")))
    rating = ma.integer(strict=True, validate=ratting_validate)


quote_schema = QuoteSchema()
quotes_schema = QuoteSchema(many=True)  

