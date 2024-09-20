from sqlalchemy_serializer import serialize_collection as sc
from services.app import db, cache
from models.books import Book
from libs.response import Response
from libs.dateutil import parse_date

NOT_FOUND_MESSAGE = "Book ID '{}' cannot be found"


class BookService:
  def __get_book_from_request(self, req):
    if not "author_id" in req.json:
      return ValueError("Missing 'author_id'")
    elif not "title" in req.json:
      return ValueError("Missing 'title'")
    elif not "description" in req.json:
      return ValueError("Missing 'description'")
    elif not "publish_date" in req.json:
      return ValueError("Missing 'publish_date'")

    title = req.json["title"].strip()
    desc = req.json["description"].strip()
    publ_date_str = req.json["publish_date"].strip()
    publish_date = parse_date(publ_date_str, "%Y-%m-%d")
    if not title:
      return ValueError("Title cannot be empty")
    elif not description:
      return ValueError("Description cannot be empty")
    elif isinstance(publish_date, ValueError):
      return ValueError("Invalid publish date '{}'".format(publ_date_str))

    return Book(author_id, title, description, publish_date)

  def __book_not_found(self, id):
    return "Book ID '{}' cannot be found".format(id)

  def __cache_key(self, id):
    return "book[{}]".format(id)

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
      return Response.bad_request(book).resp()

    db.session.add(book)
    db.session.commit()
    return Response.success(book.to_dict()).resp()

  def update_book(self, req, id):
    book = self.__get_book_from_cache(id)
    if not book:
      return self.__book_not_found(id).resp()

    params = self.__get_book_from_request(req)
    if not params:
      return self.__book_not_found(id).resp()

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

    cache.delete(self.__cache_key(id))
    return Response.success(None).resp()

bookservice = BookService()
