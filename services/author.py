from sqlalchemy_serializer import serialize_collection as sc
from services.app import db, cache
from models.authors import Author
from libs.response import Response
from libs.dateutil import parse_date


class AuthorService:
  def __get_author_from_request(self, req):
    if not "name" in req.json:
      return ValueError("Missing 'name'")
    elif not "bio" in req.json:
      return ValueError("Missing 'bio'")
    elif not "birth_date" in req.json:
      return ValueError("Missing birth date")

    name = req.json["name"].strip()
    bio = req.json["bio"].strip()
    birth_date_str = str(req.json["birth_date"]).strip()
    birth_date = parse_date(birth_date_str, "%Y-%m-%d")
    if not name:
      return ValueError("Name cannot be empty")
    elif not bio:
      return ValueError("Bio cannot be empty")
    elif not birth_date_str:
      return ValueError("Birth date cannot be empty")
    elif isinstance(birth_date, ValueError):
      return ValueError("Invalid birth date: '{}'".format(birth_date_str))

    return Author(name, bio, birth_date)

  def __author_not_found(self, id):
    return Response.not_found("Author ID '{}' cannot be found".format(id))

  def __author_cache_key(self, id):
    return "author[{}]".format(id)

  def __books_cahe_key(self, id):
    return "books_from[{}]".format(id)

  def __get_author_from_cache(self, id):
    def onmiss(k):
      return Author.query.get(id)

    return cache.get(self.__author_cache_key(id), onmiss)

  def __delete_author_from_cache(self, id):
    cache.delete(self.__author_cache_key(id))

  def list_authors(self, req):
    def onmiss(k):
      return Author.query.all()

    authors = cache.get(self.__author_cache_key(id), onmiss)
    return Response.success(sc(authors)).resp()

  def get_author(self, req, id):
    author = self.__get_author_from_cache(id)
    if not author:
      return self.__author_not_found(id).resp()

    return Response.success(author.to_dict()).resp()

  def add_new_author(self, req):
    author = self.__get_author_from_request(req)
    if isinstance(author, Exception):
      return Response.bad_request(str(author)).resp()
    else:
      db.session.add(author)
      db.session.commit()
      return Response.success(author.to_dict()).resp()

  def update_author(self, req, id):
    author = self.__get_author_from_cache(id)
    if not author:
      return self.__author_not_found(id).resp()

    params = self.__get_author_from_request(req)
    if isinstance(params, ValueError):
      return Response.bad_request(str(params))

    author.name = params.name
    author.bio = params.bio
    db.session.commit()
    cache.update(self.__author_cache_key(id), author)
    return Response.success(author.to_dict()).resp()

  def delete_author(self, req, id):
    author = self.__get_author_from_cache(id)
    if not author:
      return self.__author_not_found(id).resp()

    db.session.delete(author)
    db.session.commit()
    self.__delete_author_from_cache(id)
    return Response.success(None)

  def list_book_from_author(self, req, id):
    author = self.__get_author_from_cache(id)
    if not author:
      return self.__author_not_found(id).resp()
    
    def onmiss(k):
      return author.books

    books = cache.get(self.__books_cahe_key(id), onmiss)
    return Response.success(sc(books)).resp()

authorservice = AuthorService()
