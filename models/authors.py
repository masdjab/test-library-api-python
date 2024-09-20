from services.app import db
from sqlalchemy_serializer import SerializerMixin


class Author(db.Model, SerializerMixin):
  __tablename__ = "authors"
  serialize_only = ('id', 'name', 'bio', 'birth_date')

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30))
  bio = db.Column(db.String(200))
  birth_date = db.Column(db.DateTime())
  books = db.relationship('models.books.Book', cascade="all,delete", backref='author')

  def __init__(self, name, bio, birth_date):
    self.name = name
    self.bio = bio
    self.birth_date = birth_date

  def __repr__(self):
    return '<id {}>'.format(self.id)
