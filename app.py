from flask import request
from werkzeug.exceptions import HTTPException
from libs.config import config
from libs.response import Response
from services.app import app, logger
from services.author import authorservice as authors
from services.book import bookservice as books


# author API routes
@app.route("/api/v1/authors", methods=["GET"])
def list_authors():
  return authors.list_authors(request)

@app.route("/api/v1/authors", methods=["POST"])
def post_author():
  return authors.add_new_author(request)

@app.route("/api/v1/authors/<int:id>", methods=["GET"])
def get_author(id):
  return authors.get_author(request, id)

@app.route("/api/v1/authors/<int:id>", methods=["PUT"])
def put_author(id):
  return authors.update_author(request, id)

@app.route("/api/v1/authors/<int:id>", methods=["DELETE"])
def delete_author(id):
  return authors.delete_author(request, id)

@app.route("/api/v1/authors/<int:id>/books", methods=["GET"])
def list_books_from_author(id):
  return authors.list_book_from_author(request, id)

# book API routes
@app.route("/api/v1/books", methods=["GET"])
def list_books():
  return books.list_books(request)

@app.route("/api/v1/books", methods=["POST"])
def post_book():
  return books.add_new_book(request)

@app.route("/api/v1/books/<int:id>", methods=["GET"])
def get_book(id):
  return books.get_book(request, id)

@app.route("/api/v1/books/<int:id>", methods=["PUT"])
def patch_book(id):
  return books.update_book(request, id)

@app.route("/api/v1/books/<int:id>", methods=["DELETE"])
def delete_book():
  return books.delete_book(request, id)

# miscellaneous routes
@app.route("/ping", methods=["GET"])
def ping():
  return "PONG"

@app.errorhandler(HTTPException)
def handle_exception(e):
  return Response.error(e.code, e.description).resp()


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=config.app_port)
