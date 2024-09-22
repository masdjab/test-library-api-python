from sqlalchemy_serializer import SerializerMixin
from services.app import db


MAX_TITLE_LENGTH        = 50
MAX_DESCRIPTION_LENGTH  = 200


class Book(db.Model, SerializerMixin):
    __tablename__ = "books"
    serialize_only = ('id', 'author_id', 'title', 'description', 'publish_date')

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), unique=False, nullable=False)
    title = db.Column(db.String(MAX_TITLE_LENGTH))
    description = db.Column(db.String(MAX_DESCRIPTION_LENGTH))
    publish_date = db.Column(db.DateTime())

    def __init__(self, author_id, title, description, publish_date):
        self.author_id = author_id
        self.title = title
        self.description = description
        self.publish_date = publish_date

    def __repr__(self):
        return f"<id {self.id}>"

    @staticmethod
    def max_title_length():
        return MAX_TITLE_LENGTH

    @staticmethod
    def max_description_length():
        return MAX_DESCRIPTION_LENGTH
