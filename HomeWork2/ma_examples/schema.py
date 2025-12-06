from marshmallow import Schema, fields


class AuthorSchema(Schema):
    id = fields.Integer()
    name =fields.String()
    email = fields.Email()
 
