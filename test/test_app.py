"""Unit test to make sure all enpoints working as expected"""

import datetime
import json
from unittest import TestCase, mock
from services.app import cache
from app import app
from models.authors import Author
from models.books import Book


class TestApp(TestCase):
    """Test all endpoints' functionality"""
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        self.author_dict_sample = {
            "name":           "somename",
            "bio":            "somebio",
            "birth_date":     "1984-10-12",
        }
        self.author_obj_sample = Author("someone", "somebio", datetime.datetime(1984, 10, 12))
        self.author_obj_sample.id = 1
        self.book_dict_sample = {
            "author_id":      1,
            "title":          "Some Title",
            "description":    "Some Description",
            "publish_date":   "2000-01-01",
        }
        self.book_obj_sample = Book(1, "Some Title", "Some Description",
            datetime.datetime(2000, 1, 1))

    def tearDown(self):
        self.ctx.pop()

    def __saved_authors(self):
        return [
            Author("Name 1", "bio 1", datetime.datetime(1980, 1, 2)),
            Author("Name 2", "bio 2", datetime.datetime(1980, 1, 2)),
            Author("Name 3", "bio 3", datetime.datetime(1980, 1, 3)),
        ]

    def __saved_books(self):
        return [
            Book(1, "Title 1", "some desc", datetime.datetime(2000, 1, 1)),
            Book(2, "Title 2", "some desc", datetime.datetime(2000, 1, 2)),
            Book(3, "Title 3", "some desc", datetime.datetime(2000, 1, 2)),
        ]

    def __invalid_author_params(self):
        return [
            {
                "desc": "Must fail when name missing",
                "data": {},
                "message": "Missing 'name'",
            },
            {
                "desc": "Must fail when bio missing",
                "data": {"name": ""},
                "message": "Missing 'bio'",
            },
            {
                "desc": "Must fail when birth date missing",
                "data": {"name": "", "bio": ""},
                "message": "Missing 'birth_date'",
            },
            {
                "desc": "Must fail when name empty",
                "data": {"name": "   ", "bio": "", "birth_date": ""},
                "message": "Name cannot be empty",
            },
            {
                "desc": "Must fail when bio empty",
                "data": {"name": "Name 1", "bio": "    ", "birth_date": ""},
                "message": "Bio cannot be empty",
            },
            {
                "desc": "Must fail when birth date empty",
                "data": {"name": "Name 1", "bio": "abc", "birth_date": "    "},
                "message": "Birth date cannot be empty",
            },
            {
                "desc": "Must fail when name too long",
                "data": {"name": "x" * (Author.max_name_length() + 1),
                    "bio": "abc", "birth_date": "xyz"},
                "message": f"Name too long, max {Author.max_name_length()} chars",
            },
            {
                "desc": "Must fail when bio too long",
                "data": {"name": "Name 1",
                    "bio": "x" * (Author.max_bio_length() + 1), "birth_date": "xyz"},
                "message": f"Bio too long, max {Author.max_bio_length()} chars",
            },
            {
                "desc": "Must fail when birth date invalid 1",
                "data": {"name": "Name 1", "bio": "somebio", "birth_date": "xyz"},
                "message": "Invalid birth date: 'xyz'",
            },
            {
                "desc": "Must fail when birth date invalid 2",
                "data": {"name": "Name 1", "bio": "somebio", "birth_date": "2000"},
                "message": "Invalid birth date: '2000'",
            },
            {
                "desc": "Must fail when birth date invalid 3",
                "data": {"name": "Name 1", "bio": "somebio", "birth_date": "2000-20-20"},
                "message": "Invalid birth date: '2000-20-20'",
            },
        ]

    def __invalid_book_params(self):
        return [
            {
                "desc": "Must fail when author_id missing",
                "data": {},
                "message": "Missing 'author_id'"
            },
            {
                "desc": "Must fail when title missing",
                "data": {"author_id": 1},
                "message": "Missing 'title'"
            },
            {
                "desc": "Must fail when description missing",
                "data": {"author_id": 1, "title": ""},
                "message": "Missing 'description'"
            },
            {
                "desc": "Must fail when publish_date missing",
                "data": {"author_id": 1, "title": "", "description": ""},
                "message": "Missing 'publish_date'"
            },
            {
                "desc": "Must fail when title empty",
                "data": {"author_id": 1, "title": "      ", "description": "", "publish_date": ""},
                "message": "Title cannot be empty"
            },
            {
                "desc": "Must fail when title too long",
                "data": {"author_id": 1, "title": "x" * (Book.max_title_length() + 1),
                    "description": "", "publish_date": ""},
                "message": f"Title too long, max {Book.max_title_length()} chars"
            },
            {
                "desc": "Must fail when description empty",
                "data": {"author_id": 1, "title": "  some title  ",
                    "description": "     ", "publish_date": ""},
                "message": "Description cannot be empty"
            },
            {
                "desc": "Must fail when description too long",
                "data": {"author_id": 1, "title": "  some title  ",
                    "description": "x" * (Book.max_description_length() + 1), "publish_date": ""},
                "message": f"Description too long, max {Book.max_description_length()} chars"
            },
            {
                "desc": "Must fail when publish date empty",
                "data": {"author_id": 1, "title": "  some title  ",
                    "description": "  a  ", "publish_date": "     "},
                "message": "Invalid publish date ''"
            },
            {
                "desc": "Must fail when publish date invalid 1",
                "data": {"author_id": 1, "title": "abc", "description": "def",
                    "publish_date": "pqrs"},
                "message": "Invalid publish date 'pqrs'"
            },
            {
                "desc": "Must fail when publish date invalid 2",
                "data": {"author_id": 1, "title": "abc", "description": "def",
                    "publish_date": "2000"},
                "message": "Invalid publish date '2000'"
            },
            {
                "desc": "Must fail when publish date invalid 2",
                "data": {"author_id": 1, "title": "abc", "description": "def",
                    "publish_date": "2000-21-10"},
                "message": "Invalid publish date '2000-21-10'"
            },
        ]

    @mock.patch("models.authors.Author.query")
    def test_list_authors(self, mock_query):
        """Test get all authors, should return 200"""
        expected_data = [a.to_dict() for a in self.__saved_authors()]
        mock_query.all.return_value = self.__saved_authors()
        cache.delete("author[]")
        resp = self.client.get("/api/v1/authors")
        body = json.loads(resp.get_data(as_text=True))
        mock_query.all.assert_called_once()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["data"], expected_data)

    @mock.patch("models.authors.Author.query")
    def test_get_author_success(self, mock_query):
        """Test get author by ID, should return 200"""
        expected_data = self.author_obj_sample.to_dict()
        mock_query.get.return_value = self.author_obj_sample
        cache.delete("author[1]")
        resp = self.client.get("/api/v1/authors/1")
        body = json.loads(resp.get_data(as_text=True))
        mock_query.get.assert_called_with(1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["data"], expected_data)

    @mock.patch("models.authors.Author.query")
    def test_get_author_not_found(self, mock_query):
        """Test GET non-existing author, should return 404"""
        mock_query.get.return_value = None
        cache.delete("author[1]")
        resp = self.client.get("/api/v1/authors/1")
        body = json.loads(resp.get_data(as_text=True))
        mock_query.get.assert_called_with(1)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(body["data"], None)

    @mock.patch("services.author.db")
    def test_post_author_success(self, mock_db):
        """Test POST author, should return 200 when successful"""
        resp = self.client.post("/api/v1/authors",
            data=json.dumps(self.author_dict_sample),
            content_type="application/json")
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        self.assertEqual(resp.status_code, 200)

    @mock.patch("services.author.db")
    def test_post_author_failed(self, mock_db):
        """Test POST author with invalid parameters, should return 400"""
        for p in self.__invalid_author_params():
            resp = self.client.post("/api/v1/authors",
                data=json.dumps(p["data"]),
                content_type="application/json")
            body = json.loads(resp.get_data(as_text=True))
            mock_db.session.add.assert_not_called()
            mock_db.session.commit.assert_not_called()
            self.assertEqual(resp.status_code, 400, p["desc"])
            self.assertEqual(body["meta"]["message"], p["message"], p["desc"])

    @mock.patch("models.authors.Author.query")
    @mock.patch("services.author.db")
    def test_put_author_success(self, mock_db, mock_query):
        """Test PUT author, should return 200 on successful"""
        mock_query.get.return_value = self.author_obj_sample
        cache.delete("author[1]")
        resp = self.client.put("/api/v1/authors/1",
            data=json.dumps(self.author_dict_sample),
            content_type="application/json")
        mock_db.session.commit.assert_called_once()
        self.assertEqual(resp.status_code, 200)

    @mock.patch("services.author.db")
    @mock.patch("models.authors.Author.query")
    def test_put_author_failed(self, mock_query, mock_db):
        """Test PUT author with invalid parameters, should return 400"""
        mock_query.get.return_value = self.author_obj_sample
        cache.delete("author[1]")

        for p in self.__invalid_author_params():
            cache.delete("author[1]")
            resp = self.client.put("/api/v1/authors/1",
                data=json.dumps(p["data"]),
                content_type="application/json")
            body = json.loads(resp.get_data(as_text=True))
            mock_db.session.commit.assert_not_called()
            self.assertEqual(resp.status_code, 400, p["desc"])
            self.assertEqual(body["meta"]["message"], p["message"], p["desc"])

    @mock.patch("services.author.db")
    @mock.patch("models.authors.Author.query")
    def test_delete_author_success(self, mock_query, mock_db):
        """Test DELETE author, should return 200 on successful"""
        mock_query.get.return_value = self.author_obj_sample
        cache.delete("author[1]")
        resp = self.client.delete("/api/v1/authors/1")
        mock_db.session.delete.assert_called_once()
        mock_db.session.commit.assert_called_once()
        self.assertEqual(resp.status_code, 200)

    @mock.patch("services.author.db")
    @mock.patch("models.authors.Author.query")
    def test_delete_author_failed(self, mock_query, mock_db):
        """Test DELETE non-existing author, should return 404"""
        mock_query.get.return_value = None
        cache.delete("author[1]")
        resp = self.client.delete("/api/v1/authors/1")
        mock_db.session.delete.assert_not_called()
        mock_db.session.commit.assert_not_called()
        self.assertEqual(resp.status_code, 404)

    @mock.patch("models.authors.Author.query")
    def test_get_books_from_author_success(self, mock_query):
        """Test GET list of books from particular author, should return 200 on successful"""
        mock_query.get.return_value = self.author_obj_sample
        cache.delete("author[1]")
        resp = self.client.get("/api/v1/authors/1/books")
        self.assertEqual(resp.status_code, 200)

    @mock.patch("models.authors.Author.query")
    def test_get_books_from_author_failed(self, mock_query):
        """Test GET list of books from non existing author, should return 404"""
        mock_query.get.return_value = None
        cache.delete("author[1]")
        resp = self.client.get("/api/v1/authors/1/books")
        self.assertEqual(resp.status_code, 404)

    @mock.patch("models.books.Book.query")
    def test_list_books(self, mock_query):
        """Test GET all books, should return 200 when successful"""
        expected_data = [a.to_dict() for a in self.__saved_books()]
        mock_query.all.return_value = self.__saved_books()
        cache.delete("book[]")
        resp = self.client.get("/api/v1/books")
        body = json.loads(resp.get_data(as_text=True))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["data"], expected_data)

    @mock.patch("models.books.Book.query")
    def test_get_book_success(self, mock_query):
        """Test GET book by id, should return 200 when successful"""
        expected_data = self.book_obj_sample.to_dict()
        mock_query.get.return_value = self.book_obj_sample
        cache.delete("book[1]")
        resp = self.client.get("/api/v1/books/1")
        body = json.loads(resp.get_data(as_text=True))
        mock_query.get.assert_called_with(1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["data"], expected_data)

    @mock.patch("models.books.Book.query")
    def test_get_book_not_found(self, mock_query):
        """Test GET non-existing book, should return 404"""
        mock_query.get.return_value = None
        cache.delete("book[1]")
        resp = self.client.get("/api/v1/books/1")
        body = json.loads(resp.get_data(as_text=True))
        mock_query.get.assert_called_with(1)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(body["data"], None)

    @mock.patch("services.book.db")
    @mock.patch("models.authors.Author.query")
    def test_post_book_success(self, mock_author, mock_db):
        """Test POST book, should return 200 when successful"""
        mock_author.get.return_value = self.author_obj_sample
        resp = self.client.post("/api/v1/books",
            data=json.dumps(self.book_dict_sample),
            content_type="application/json")
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        self.assertEqual(resp.status_code, 200)

    @mock.patch("services.book.db")
    def test_post_book_validation_failed(self, mock_db):
        """Test POST book with invalid parameters, should return 400"""
        for p in self.__invalid_book_params():
            resp = self.client.post("/api/v1/books",
                data=json.dumps(p["data"]),
                content_type="application/json")
            body = json.loads(resp.get_data(as_text=True))
            mock_db.session.add.assert_not_called()
            mock_db.session.commit.assert_not_called()
            self.assertEqual(resp.status_code, 400, p["desc"])
            self.assertEqual(body["meta"]["message"], p["message"], p["desc"])

    @mock.patch("services.book.db")
    @mock.patch("models.authors.Author.query")
    def test_post_book_invalid_author(self, mock_author, mock_db):
        """Test POST book with invalid author, should return 400"""
        mock_author.get.return_value = None
        resp = self.client.post("/api/v1/books",
            data=json.dumps(self.book_dict_sample),
            content_type="application/json")
        body = json.loads(resp.get_data(as_text=True))
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(body["meta"]["message"], "Author ID '1' is not in database")

    @mock.patch("services.book.db")
    @mock.patch("models.authors.Author.query")
    @mock.patch("models.books.Book.query")
    def test_put_book_success(self, mock_book, mock_author, mock_db):
        """Test PUT book, should return 200 when successful"""
        mock_book.get.return_value = self.book_obj_sample
        mock_author.get.return_value = self.author_obj_sample
        cache.delete("book[1]")
        resp = self.client.put("/api/v1/books/1",
            data=json.dumps(self.book_dict_sample),
            content_type="application/json")
        mock_db.session.commit.assert_called_once()
        self.assertEqual(resp.status_code, 200)

    @mock.patch("services.book.db")
    @mock.patch("models.authors.Author.query")
    @mock.patch("models.books.Book.query")
    def test_put_book_validation_failed(self, mock_book, mock_author, mock_db):
        """Test PUT book with invalid parameters, should return 400"""
        mock_book.get.return_value = self.book_obj_sample
        mock_author.get.return_value = self.author_obj_sample
        for p in self.__invalid_book_params():
            cache.delete("book[1]")
            resp = self.client.put("/api/v1/books/1",
                data=json.dumps(p["data"]),
                content_type="application/json")
            body = json.loads(resp.get_data(as_text=True))
            mock_db.session.add.assert_not_called()
            mock_db.session.commit.assert_not_called()
            self.assertEqual(resp.status_code, 400, p["desc"])
            self.assertEqual(body["meta"]["message"], p["message"], p["desc"])

    @mock.patch("services.book.db")
    @mock.patch("models.authors.Author.query")
    @mock.patch("models.books.Book.query")
    def test_put_book_invalid_author(self, mock_book, mock_author, mock_db):
        """Test PUT book with invalid author, should return 400"""
        mock_book.get.return_value = self.book_obj_sample
        mock_author.get.return_value = None
        cache.delete("book[1]")
        resp = self.client.put("/api/v1/books/1",
            data=json.dumps(self.book_dict_sample),
            content_type="application/json")
        body = json.loads(resp.get_data(as_text=True))
        mock_db.session.commit.assert_not_called()
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(body["meta"]["message"], "Author ID '1' is not in database")

    @mock.patch("services.book.db")
    @mock.patch("models.books.Book.query")
    def test_delete_book_success(self, mock_query, mock_db):
        """Test DELETE book, should return 200 when successful"""
        mock_query.get.return_value = self.book_obj_sample
        cache.delete("book[1]")
        resp = self.client.delete("/api/v1/books/1")
        mock_db.session.delete.assert_called_once()
        mock_db.session.commit.assert_called_once()
        self.assertEqual(resp.status_code, 200)

    @mock.patch("services.book.db")
    @mock.patch("models.books.Book.query")
    def test_delete_book_failed(self, mock_query, mock_db):
        """Test DELETE non existing book, should return 404"""
        mock_query.get.return_value = None
        cache.delete("book[1]")
        resp = self.client.delete("/api/v1/books/1")
        body = json.loads(resp.get_data(as_text=True))
        mock_db.session.delete.assert_not_called()
        mock_db.session.commit.assert_not_called()
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(body["meta"]["message"], "Book ID '1' cannot be found")

    def test_non_json_body(self):
        """Test POST/PUT without content type being application/json, should return 415"""
        resp = self.client.post("/api/v1/authors")
        body = json.loads(resp.get_data(as_text=True))
        self.assertEqual(resp.status_code, 415)
        self.assertEqual(body["meta"]["message"], "Content type must be 'application/json'")

        resp = self.client.put("/api/v1/authors/1")
        body = json.loads(resp.get_data(as_text=True))
        self.assertEqual(resp.status_code, 415)
        self.assertEqual(body["meta"]["message"], "Content type must be 'application/json'")

    def test_invalid_json_body(self):
        """Test POST/PUT with invalid json body, should return 400"""
        resp = self.client.post("/api/v1/authors", data="{", content_type="application/json")
        body = json.loads(resp.get_data(as_text=True))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(body["meta"]["message"], "Invalid JSON body")

        resp = self.client.put("/api/v1/authors/1", data="{", content_type="application/json")
        body = json.loads(resp.get_data(as_text=True))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(body["meta"]["message"], "Invalid JSON body")

    def test_ping(self):
        """Test ping, should always return 200"""
        resp = self.client.get("/ping")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_data(as_text=True), "PONG")
