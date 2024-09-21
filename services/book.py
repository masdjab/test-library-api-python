from sqlalchemy_serializer import serialize_collection as sc
from services.app import db, cache, logger
from models.authors import Author
from models.books import Book
from libs.response import Response
from libs.dateutil import parse_date

NOT_FOUND_MESSAGE = "Book ID '{}' cannot be found"


class BookService:
  def __get_book_from_request(self, req):
    try:
      if not "author_id" in req.json:
        return ValueError("Missing 'author_id'")
      elif not "title" in req.json:
        return ValueError("Missing 'title'")
      elif not "description" in req.json:
        return ValueError("Missing 'description'")
      elif not "publish_date" in req.json:
        return ValueError("Missing 'publish_date'")

      author_id = req.json["author_id"]
      title = req.json["title"].strip()
      description = req.json["description"].strip()
      publ_date_str = req.json["publish_date"].strip()
      publish_date = parse_date(publ_date_str[0:10], "%Y-%m-%d")
      if not title:
        return ValueError("Title cannot be empty")
      elif len(title) > Book.max_title_length():
        return ValueError("Title too long, max {} chars".format(Book.max_title_length()))
      elif not description:
        return ValueError("Description cannot be empty")
      elif len(description) > Book.max_description_length():
        return ValueError("Description too long, max {} chars".format(Book.max_description_length()))
      elif isinstance(publish_date, ValueError):
        return ValueError("Invalid publish date '{}'".format(publ_date_str))

      author = Author.query.get(author_id)
      if not author:
        return ValueError("Author ID '{}' is not in database".format(author_id))

      return Book(author_id, title, description, publish_date)
    except Exception as e:
      logger.fatal("Unexpected error in services.BookService.__get_book_from_request: {}".format(
        str(e)))
      return e

  def __book_not_found(self, id):
    return "Book ID '{}' cannot be found".format(id)

  def __cache_key(self, id):
    return "book[{}]".format(str(id) if id else "")

  def __get_book_from_cache(self, id):
    def onmiss(k):
      return Book.query.get(id)

    return cache.get(self.__cache_key(id), onmiss)

  def list_books(self, req):
    def onmiss(k):
      return Book.query.all()

    books = cache.get(self.__cache_key(id), onmiss)
    return Response.success(sc(books)).resp()

  def get_book(self, req, id):
    book = self.__get_book_from_cache(id)
    if not book:
      return self.__book_not_found(id).resp()

    return Response.success(book.to_dict()).resp()

  def add_new_book(self, req):
    book = self.__get_book_from_request(req)
    if isinstance(book, ValueError):
      return Response.bad_request(str(book)).resp()
    elif isinstance(book, Exception):
      return Response.internal_server_error("Unexpected error").resp()

    db.session.add(book)
    db.session.commit()
    return Response.success(book.to_dict()).resp()

  def update_book(self, req, id):
    book = self.__get_book_from_cache(id)
    if not book:
      return self.__book_not_found(id).resp()
    elif isinstance(book, Exception):
      return Response.internal_server_error("Unexpected error").resp()

    params = self.__get_book_from_request(req)
    if isinstance(book, ValueError):
      return Response.bad_request(str(book)).resp()

    book.author_id = params.author_id
    book.title = params.title
    book.description = params.description
    book.publish_date = params.publish_date
    db.session.commit()
    cache.update(self.__cache_key(id), book)
    return Response.success(book.to_dict()).resp()

  def delete_book(self, req, id):
    book = self.__get_book_from_cache(id)
    if not book:
      return self.__book_not_found(id).resp()

    db.session.delete(book)
    db.session.commit()
    cache.delete(self.__cache_key(id))
    return Response.success(None).resp()

bookservice = BookService()
