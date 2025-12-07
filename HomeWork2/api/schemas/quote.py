from marshmallow import EXCLUDE
from api import ma
from api.models.quote import QuoteModel
from api.schemas.author import AuthorSchema
from marshmallow.validate import Range



def rating_validate(value:int):
    """ Функция возвращает проверку допустимого диапазона rating"""
    # Если  rating в допустимом диапазоне то возвращается True
    return value in range (1,6)


class QuoteSchema(ma.SQLAlchemySchema):
    class Meta:
        model = QuoteModel
        unknown = EXCLUDE
        dump_only =("id",)

 
    id = ma.auto_field()
    text = ma.auto_field(required = True)
    author_id = ma.auto_field()
    author = ma.Nested(AuthorSchema(only=("name","surname",))) # указываем поля для отображения из связанной таблицы
    rating = ma.Integer(strict=True, validate=Range(min=1, max=5))


quote_schema = QuoteSchema(exclude=["author_id"])
quotes_schema = QuoteSchema(many=True, exclude=["author"])  
edit_quotes_schema= QuoteSchema(load_instance=False)
# если при обновлении пришел неправильный рейтинг, то используем схему без рейтинга
edit_quotes_schema_non_rating= QuoteSchema(load_instance=False, exclude=["rating"], partial = True) 

