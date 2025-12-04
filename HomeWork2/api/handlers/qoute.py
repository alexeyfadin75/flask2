
from api import app, db
from flask import abort, jsonify, request
from api.models.qoute import QuoteModel
from api.models.author import AuthorModel
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError
from . import check

@app.get("/quotes")
def get_quotes():
    """ Функция возвращает все цитаты из БД. """
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    # Формируем список словарей
    quotes = []
    for quote in quotes_db:
        quotes.append(quote.to_dict())
    return jsonify(quotes), 200

# URL: "/authors/<int:author_id>/quotes"
@app.route("/authors/<int:author_id>/quotes", methods=["GET", "POST"])
def author_quotes(author_id: int):
    author = db.get_or_404(AuthorModel, author_id, description=f"Author with id={author_id} not found")

    if request.method == "GET":
        quotes = [quote.to_dict() for quote in author.quotes]
        return jsonify({"author": author.name} | {"quotes": quotes}), 200

    elif request.method == "POST":
        data = request.json
        new_quote = QuoteModel(author, **data)
        db.session.add(new_quote)
        db.session.commit()
        return jsonify(new_quote.to_dict() | { "author_id" : author.id}), 201
    else:
        abort(405)




# ====== Quotes endpoints =======


@app.get("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id: int):
    """ Return quote by id from db."""
    quote = db.get_or_404(entity=QuoteModel, ident=quote_id, description=f"Quote with id={quote_id} not found")
    return jsonify(quote.to_dict()), 200



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
        quote = QuoteModel(**data)
        db.session.add(quote)
        db.session.commit()
    except TypeError:
        abort(400, f"Invalid data. Required: <author> and <text>. Received: {', '.join(data.keys())}")
    except Exception as e:
        abort(503, f"Database error: {str(e)}")
    
    return jsonify(quote.to_dict()), 201
    



@app.put("/quotes/<int:quote_id>")
def edit_quote(quote_id: int):
    """ Update an existing quote """
    new_data = request.json
    result = check(new_data, check_rating=True)
    if not result[0]:
        return abort(400, result[1].get('error'))
    
    quote = db.get_or_404(entity=QuoteModel, ident=quote_id, description=f"Quote with id={quote_id} not found")

    try:
        for key_as_attr, value in new_data.items():
            setattr(quote, key_as_attr, value)

        db.session.commit()
        return jsonify(quote.to_dict()), 200
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
    
    
@app.route("/quotes/filter", methods=['GET'])
def filter_quotes():
    data = request.args # get query parameters from URL
    try:
        quotes = db.session.scalars(db.select(QuoteModel).filter_by(**data)).all()
    except InvalidRequestError:
        abort(400, f"Invalid data. Required: <author> and <text>. Received: {', '.join(data.keys())}")
    
    return jsonify([quote.to_dict() for quote in quotes]), 200    