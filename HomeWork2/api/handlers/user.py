from flask import abort, jsonify, request
from marshmallow import ValidationError
from api import app, db
from api.models.user import UserModel
from api.schemas.user import user_schema



#url /users/<int:user_id> - GET
@app.get("/users/<int:user_id>")
def get_user_by_id(user_id: int):
    """ Вывод user по его id."""
    user = db.get_or_404(entity=UserModel, ident=user_id, description=f"User with id={user_id} not found")
    # return jsonify(author.to_dict()), 200 
    return user_schema.dump(user), 200   

#url /users- GET
@app.get("/users")
def get_users():
    """ Функция возвращает всех users из БД. """
    users_db = db.session.scalars(db.select(UserModel)).all()
    return user_schema.dump(users_db, many=True), 200      


#url /users - POST
@app.post("/users")
def create_user(user_id: int):
    try:
        request_data = request.get_data()   # возвращает сырые данные
        user = user_schema.loads(request_data) # для сырых данных  с loads
        user.save()
    except ValidationError as ve:
        db.session.rollback()
        abort(400, f" Ошибка валидации {str(ve)}")    
    except Exception as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")
    return jsonify(user_schema.dump(user)), 201