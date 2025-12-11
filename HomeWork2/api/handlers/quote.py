
from marshmallow import EXCLUDE, ValidationError
from api import app, db,auth
from flask import abort, jsonify, request
from api.models.quote import QuoteModel
from api.models.author import AuthorModel
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError
#from . import check
from api.schemas.quote import quotes_schema, quote_schema, edit_quotes_schema_non_rating, edit_quotes_schema

@app.get("/quotes")
def get_quotes():
    """ Функция возвращает все цитаты из БД. """
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    # Формируем список словарей
    # quotes = []
    # for quote in quotes_db:
    #     quotes.append(quote.to_dict())
    return jsonify(quotes_schema.dump(quotes_db)), 200

# URL: "/authors/<int:author_id>/quotes"
@app.route("/authors/<int:author_id>/quotes", methods=["GET", "POST"])
@auth.login_required
def author_quotes(author_id: int):
    print("user=", auth.current_user())
    author = db.get_or_404(AuthorModel, author_id, description=f"Author with id={author_id} not found")
    
    if request.method == "GET":
        #GET: Получение всех цитат автора

        # Вариант A: Используем схему для сериализации
        quotes = author.quotes  # Это уже список объектов QuoteModel
        return jsonify({
            "name": author.name, 
            "surname": author.surname,
            "author_id": author.id,
            "quotes": quotes_schema.dump(quotes)  # quotes уже список
        }), 200
        
        # Вариант B: Если нужны данные автора в каждой цитате
        # quotes_data = quotes_schema.dump(author.quotes)
        # return jsonify(quotes_data), 200

        # quotes = [quote.to_dict() for quote in author.quotes]
        # return jsonify({"author": author.name} | quotes_schema.dump(quotes)), 200

    elif request.method == "POST":
         # POST: Создание новой цитаты для автора
        try:
            data = quote_schema.loads(request.data)
            new_quote = QuoteModel(author, **data)
            db.session.add(new_quote)
            db.session.commit()
            return jsonify(quote_schema.dump(new_quote)), 201
        except ValidationError as ve:
            db.session.rollback()
            # Проверяем, связана ли ошибка с полем rating
            rating_error = False
            if hasattr(ve, 'messages_dict'):
                # Для Marshmallow 3.x структура
                if 'rating' in ve.messages_dict:
                    rating_error = True
            if rating_error:
                json_data = request.get_json()
                json_data.pop('rating', None)  # Удаляем рейтинг из данных
                data = edit_quotes_schema_non_rating.load(json_data)
                new_quote = QuoteModel(author, **data)
                db.session.add(new_quote)
                db.session.commit()
                return jsonify(quote_schema.dump(new_quote)), 201
            else:
                db.session.rollback()
                abort(400, ve)
    else:
        abort(405)




# ====== Quotes endpoints =======


@app.get("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id: int):
    """ Return quote by id from db."""
    quote = db.get_or_404(entity=QuoteModel, ident=quote_id, description=f"Quote with id={quote_id} not found")
    return jsonify(quote_schema.dump(quote)), 200



@app.get("/quotes/count")
def get_quotes_count() -> int:
    """ Return count of quotes in db."""
    count = db.session.scalar(func.count(QuoteModel.id))
    return jsonify(count=count), 200


@app.post("/quotes")
def create_quote():
    """ Function creates new quote and adds it to db."""
    data = request.json
    try:
        quote = quote_schema.load(data)
        #quote = QuoteModel(**data)
        db.session.add(quote)
        db.session.commit()
    except ValidationError as ve:
        abort(400, f": {str(ve)}")
    except Exception as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")
    
    return jsonify(quote_schema.dump(quote)), 201
    



@app.put("/quotes/<int:quote_id>")
def edit_quote(quote_id: int):
    """ Update an existing quote """
     # Сначала получаем существующую цитату
    quote = db.get_or_404(entity=QuoteModel, ident=quote_id, description=f"Quote with id={quote_id} not found")
    print(quote)
    
    try: 
         # Пробуем загрузить данные с валидацией
        new_data = edit_quotes_schema.load(request.json, partial=True, unknown = EXCLUDE)
        # # Обновляем поля цитаты
        for key_as_attr, value in new_data.items():
            setattr(quote, key_as_attr, value)
        
        db.session.commit()
        return jsonify(quote_schema.dump(quote)), 200
    
    except ValidationError as ve:
            db.session.rollback()
            # Проверяем, связана ли ошибка с полем rating
            rating_error = False
            if hasattr(ve, 'messages_dict'):
                # Для Marshmallow 3.x структура
                if 'rating' in ve.messages_dict:
                    rating_error = True
            if rating_error:
                json_data = request.get_json()
                json_data.pop('rating', None)  # Удаляем рейтинг из данных
                data = edit_quotes_schema_non_rating.load(json_data)  # Обновляем цитату, а не создаем новую
                for key_as_attr, value in data.items():
                    setattr(quote, key_as_attr, value)                
                db.session.commit()
                return jsonify(quote_schema.dump(quote)), 201
            else:
                db.session.rollback()
                abort(400, ve)
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
    """Delete quote by id """
    quote = db.get_or_404(entity=QuoteModel, ident=quote_id, description=f"Quote with id={quote_id} not found")
    db.session.delete(quote)
    try:
        db.session.commit()
        return jsonify({"message": f"Quote with id {quote_id} has deleted."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")
    
    
@app.route("/quotes/filterold", methods=['GET'])
def filter_quotes():
    data = request.args # get query parameters from URL
    try:
        quotes = db.session.scalars(db.select(QuoteModel).filter_by(**data)).all()
    except InvalidRequestError:
        abort(400, f"Invalid data. Received: {', '.join(data.keys())}")
    
    return jsonify(quotes_schema.dump(quotes)), 200    



@app.route("/quotes/filter", methods=['GET'])
def filter_quotes_new():
    # Получаем список всех ключей параметров
    data = request.args
    
    # базовый запрос
    query = db.select(QuoteModel)
    
    # Флаги для оптимизации запросов
    needs_author_join = any(key in ['name', 'surname'] for key in data.keys())
    
    if needs_author_join:
        query = query.join(QuoteModel.author)
    
    # Обработка фильтров
    for key, value in data.items():
        if key == 'text':
            query = query.filter(QuoteModel.text.ilike(f"%{value}%"))
        
        elif key == 'rating':
            try:
                rating = int(value)
                query = query.filter(QuoteModel.rating == rating)
            except ValueError:
                abort(400, "Rating must be an integer")
        
        elif key in ['id', 'author_id']:
            try:
                int_value = int(value)
                query = query.filter(getattr(QuoteModel, key) == int_value)
            except ValueError:
                abort(400, f"Field '{key}' must be an integer")
        
        elif key == 'name':
            query = query.filter(AuthorModel.name.ilike(f"%{value}%"))
        
        elif key == 'surname':
            query = query.filter(AuthorModel.surname.ilike(f"%{value}%"))
    
    quotes = db.session.scalars(query).all()
    return jsonify(quotes_schema.dump(quotes)), 200