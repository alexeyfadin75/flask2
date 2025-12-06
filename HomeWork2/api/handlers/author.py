from marshmallow import ValidationError, EXCLUDE
from api import app, db
from flask import request, abort, jsonify
from api.models.author import AuthorModel
from api.schemas.author import author_schema, edit_author_schema

@app.post("/authors")
def create_author():
    #"Добавление авторов"
    # add_to_db(AuthorModel, author_data)  # Variant 2
    try:
        request_data = request.get_data()   # возвращает сырые данные
        author_data = author_schema.loads(request_data) # для сырых данных  с loads
        author = AuthorModel(**author_data) #Оператор ** (двойная звездочка) распаковывает словарь в именованные аргументы:
        db.session.add(author)
        db.session.commit()
    except ValidationError as ve:
        db.session.rollback()
        abort(400, f" Ошибка валидации {str(ve)}")    
    except Exception as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")
    return jsonify(author_schema.dump(author)), 201

@app.route("/authors/<int:author_id>", methods=['DELETE'])
def delete_author(author_id):
    """Удалене авторов по id """
    author = db.get_or_404(entity=AuthorModel, ident=author_id, description=f"Author with id={author_id} not found")
    db.session.delete(author)
    try:
        db.session.commit()
        return jsonify({"message": f"Authors with id {author_id} has deleted."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")

@app.put("/authors/<int:author_id>")
def edit_authors(author_id: int):
    """ Изменение имени автора по id """
    try: 
        new_data = edit_author_schema.load(request.json, unknown = EXCLUDE)
        print(new_data)
    
        author = db.get_or_404(entity=AuthorModel, ident=author_id, description=f"Authors with id={author_id} not found")
    except ValidationError as ve:
        return abort (400,f" Ошибка проверки  {str(ve)}")

    try:
        for key_as_attr, value in new_data.items():
            setattr(author, key_as_attr, value)

        db.session.commit()
        return jsonify(author.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")

@app.route("/authors/<int:author_id>", methods=['DELETE'])
def delete_qauthors(author_id):
    """Удаление автора  id """
    author = db.get_or_404(entity=AuthorModel, ident=author_id, description=f"Authors with id={author_id} not found")
    db.session.delete(author)
    try:
        db.session.commit()
        return jsonify({"message": f"Authors with id {author_id} has deleted."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")        

@app.get("/authors//<int:author_id>")
def get_author_by_id(author_id: int):
    """ Вывод автора по его id."""
    author = db.get_or_404(entity=AuthorModel, ident=author_id, description=f"Author with id={author_id} not found")
    # return jsonify(author.to_dict()), 200 
    return author_schema.dump(author), 200    

@app.get("/authors")
def get_authors():
    """ Функция возвращает всех авторов из БД. """
    authors_db = db.session.scalars(db.select(AuthorModel)).all()

    # чтобы использовать разные схемы для одного и множества  
    #return authors_schema.dump(authors_db), 200  

    # чтобы использовать одну схемy  необходимо для множественного добавить many=True
    return author_schema.dump(authors_db, many=True), 200  