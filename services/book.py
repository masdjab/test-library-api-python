from sqlalchemy_serializer import serialize_collection as sc
from services.app import db, cache, logger
from models.authors import Author
from models.books import Book
from libs.response import Response
from libs.dateutil import parse_date

NOT_FOUND_MESSAGE = "Book ID '{}' cannot be found"


class BookService:
    def __get_book_from_request(self, req):
        """Validate request params for POST/PUT"""
        try:
            if not "author_id" in req.json:
                return ValueError("Missing 'author_id'")
            if not "title" in req.json:
                return ValueError("Missing 'title'")
            if not "description" in req.json:
                return ValueError("Missing 'description'")
            if not "publish_date" in req.json:
                return ValueError("Missing 'publish_date'")

            author_id = req.json["author_id"]
            title = req.json["title"].strip()
            description = req.json["description"].strip()
            publ_date_str = req.json["publish_date"].strip()
            publish_date = parse_date(publ_date_str[0:10], "%Y-%m-%d")
            if not title:
                return ValueError("Title cannot be empty")
            if len(title) > Book.max_title_length():
                return ValueError(f"Title too long, max {Book.max_title_length()} chars")
            if not description:
                return ValueError("Description cannot be empty")
            if len(description) > Book.max_description_length():
                errmsg = f"Description too long, max {Book.max_description_length()} chars"
                return ValueError(errmsg)
            if isinstance(publish_date, ValueError):
                return ValueError(f"Invalid publish date '{publ_date_str}'")

            author = Author.query.get(author_id)
            if not author:
                return ValueError(f"Author ID '{author_id}' is not in database")

            return Book(author_id, title, description, publish_date)
        except Exception as e:
            logger.fatal("Unexpected error in services.BookService.__get_book_from_request: %s", e)
            return e

    def __book_not_found(self, book_id):
        return Response.not_found(f"Book ID '{book_id}' cannot be found")

    def __cache_key(self, book_id):
        return f"book[{str(book_id) if book_id else ''}]"

    def __get_book_from_cache(self, book_id):
        def onmiss(_):
            return Book.query.get(book_id)

        return cache.get(self.__cache_key(book_id), onmiss)

    def list_books(self, req):
        def onmiss(_):
            return Book.query.all()

        books = cache.get(self.__cache_key(id), onmiss)
        return Response.success(sc(books)).resp()

    def get_book(self, req, book_id):
        book = self.__get_book_from_cache(book_id)
        if not book:
            return self.__book_not_found(book_id).resp()

        return Response.success(book.to_dict()).resp()

    def add_new_book(self, req):
        book = self.__get_book_from_request(req)
        if isinstance(book, ValueError):
            return Response.bad_request(str(book)).resp()
        if isinstance(book, Exception):
            raise book

        db.session.add(book)
        db.session.commit()
        return Response.success(book.to_dict()).resp()

    def update_book(self, req, book_id):
        book = self.__get_book_from_cache(book_id)
        if not book:
            return self.__book_not_found(book_id).resp()

        params = self.__get_book_from_request(req)
        if isinstance(params, ValueError):
            return Response.bad_request(str(params)).resp()
        if isinstance(params, Exception):
            raise params

        book.author_id = params.author_id
        book.title = params.title
        book.description = params.description
        book.publish_date = params.publish_date
        db.session.commit()
        cache.update(self.__cache_key(book_id), book)
        return Response.success(book.to_dict()).resp()

    def delete_book(self, req, book_id):
        book = self.__get_book_from_cache(book_id)
        if not book:
            return self.__book_not_found(book_id).resp()

        db.session.delete(book)
        db.session.commit()
        cache.delete(self.__cache_key(book_id))
        return Response.success(None).resp()

bookservice = BookService()
