from api import ma
from api.models.author import AuthorModel
from marshmallow.validate import Length

class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AuthorModel
        dump_only =("id",)
        #load_instance = True # не нужно делать  author = AuthorModel(**author_data) 
    
    name=ma.auto_field(required=True, validate=Length(1,32))
    surname=ma.auto_field(required=True, validate=Length(1,32))

author_schema = AuthorSchema()
edit_author_schema = AuthorSchema(load_instance = False, partial = True)

#authors_schema = AuthorSchema(many=True)