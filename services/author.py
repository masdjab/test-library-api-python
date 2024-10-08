from sqlalchemy_serializer import serialize_collection as sc
from services.app import db, cache, logger
from models.authors import Author
from libs.response import Response
from libs.dateutil import parse_date


class AuthorService:
    def __get_author_from_request(self, req):
        try:
            if not "name" in req.json:
                return ValueError("Missing 'name'")
            if not "bio" in req.json:
                return ValueError("Missing 'bio'")
            if not "birth_date" in req.json:
                return ValueError("Missing 'birth_date'")

            name = req.json["name"].strip()
            bio = req.json["bio"].strip()
            birth_date_str = str(req.json["birth_date"]).strip()
            birth_date = parse_date(birth_date_str[0:10], "%Y-%m-%d")
            if not name:
                return ValueError("Name cannot be empty")
            if len(name) > Author.max_name_length():
                return ValueError(f"Name too long, max {Author.max_name_length()} chars")
            if not bio:
                return ValueError("Bio cannot be empty")
            if len(bio) > Author.max_bio_length():
                return ValueError(f"Bio too long, max {Author.max_bio_length()} chars")
            if not birth_date_str:
                return ValueError("Birth date cannot be empty")
            if isinstance(birth_date, ValueError):
                return ValueError(f"Invalid birth date: '{birth_date_str}'")

            return Author(name, bio, birth_date)
        except Exception as e:
            logger.fatal("Unexpected error in services.AuthorService.__get_author_from_request: %s", str(e))
            return e

    def __author_not_found(self, id):
        return Response.not_found(f"Author ID '{str(id)}' cannot be found")

    def __author_cache_key(self, id):
        return "author[{}]".format(str(id) if id else "")

    def __books_cache_key(self, id):
        return f"books_from[{id}]"

    def __get_author_from_cache(self, id):
        def onmiss(_):
            return Author.query.get(id)

        return cache.get(self.__author_cache_key(id), onmiss)

    def list_authors(self, req):
        """API handler for GET /api/v1/authors"""
        def onmiss(_):
            return Author.query.all()

        authors = cache.get(self.__author_cache_key(None), onmiss)
        return Response.success(sc(authors)).resp()

    def get_author(self, req, id):
        """API handler for GET /api/v1/authors/<id>"""
        author = self.__get_author_from_cache(id)
        if not author:
            return self.__author_not_found(id).resp()

        return Response.success(author.to_dict()).resp()

    def add_new_author(self, req):
        """API handler for POST /api/v1/authors"""
        author = self.__get_author_from_request(req)
        if isinstance(author, ValueError):
            return Response.bad_request(str(author)).resp()
        if isinstance(author, Exception):
            raise author

        db.session.add(author)
        db.session.commit()
        return Response.success(author.to_dict()).resp()

    def update_author(self, req, id):
        """API handler for PUT /api/v1/authors/<id>"""
        author = self.__get_author_from_cache(id)
        if not author:
            return self.__author_not_found(id).resp()

        params = self.__get_author_from_request(req)
        if isinstance(params, ValueError):
            return Response.bad_request(str(params)).resp()
        if isinstance(params, Exception):
            raise params

        author.name = params.name
        author.bio = params.bio
        db.session.commit()
        cache.update(self.__author_cache_key(id), author)
        return Response.success(author.to_dict()).resp()

    def delete_author(self, req, id):
        """API handler for DELETE /api/v1/authors/<id>"""
        author = self.__get_author_from_cache(id)
        if not author:
            return self.__author_not_found(id).resp()

        db.session.delete(author)
        db.session.commit()
        cache.delete(self.__author_cache_key(id))
        return Response.success(None).resp()

    def list_book_from_author(self, req, id):
        """API handler for GET /api/v1/authors/<id>/books"""
        author = self.__get_author_from_cache(id)
        if not author:
            return self.__author_not_found(id).resp()

        def onmiss(_):
            return author.books

        books = cache.get(self.__books_cache_key(id), onmiss)
        return Response.success(sc(books)).resp()

authorservice = AuthorService()
