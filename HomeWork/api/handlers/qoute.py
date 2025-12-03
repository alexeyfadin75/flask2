
from api import app, db
from flask import jsonify, request
from api.models.qoute import QuoteModel
from api.models.author import AuthorModel 

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