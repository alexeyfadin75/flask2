from api import app, db
from flask import request, abort, jsonify
from api.models.author import AuthorModel

@app.post("/authors")
def create_author():
    #"Добавление авторов"
    author_data = request.json
    # add_to_db(AuthorModel, author_data)  # Variant 2
    try:
        author = AuthorModel(**author_data)
        db.session.add(author)
        db.session.commit()
    except TypeError:
        abort(400, f"Invalid data. Required: <name>. Received: {', '.join(author_data.keys())}")
    except Exception as e:
        abort(503, f"Database error: {str(e)}")
    return jsonify(author.to_dict()), 201

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
    new_data = request.json
    print(new_data)
    #result = check(new_data, check_rating=True)
    #if not result[0]:
    #    return abort(400, result[1].get('error'))
    
    author = db.get_or_404(entity=AuthorModel, ident=author_id, description=f"Authors with id={author_id} not found")

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
    return jsonify(author.to_dict()), 200 

@app.get("/authors")
def get_authors():
    """ Функция возвращает всех авторов из БД. """
    authors_db = db.session.scalars(db.select(AuthorModel)).all()
    # Формируем список словарей
    authors = []
    for author in authors_db:
        authors.append(author.to_dict())
    return jsonify(authors), 200       