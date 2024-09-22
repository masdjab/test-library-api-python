from sqlalchemy_serializer import SerializerMixin
from services.app import db


MAX_NAME_LENGTH = 30
MAX_BIO_LENGTH = 200


class Author(db.Model, SerializerMixin):
    __tablename__ = "authors"
    serialize_only = ('id', 'name', 'bio', 'birth_date')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_NAME_LENGTH))
    bio = db.Column(db.String(MAX_BIO_LENGTH))
    birth_date = db.Column(db.DateTime())
    books = db.relationship('models.books.Book', cascade="all,delete", backref='author')

    def __init__(self, name, bio, birth_date):
        self.name = name
        self.bio = bio
        self.birth_date = birth_date

    def __repr__(self):
        return f"<id {self.id}>"

    @staticmethod
    def max_name_length():
        return MAX_NAME_LENGTH

    @staticmethod
    def max_bio_length():
        return MAX_BIO_LENGTH
