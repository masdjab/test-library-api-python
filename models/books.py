from services.app import db
from sqlalchemy_serializer import SerializerMixin

class Book(db.Model, SerializerMixin):
  __tablename__ = "books"
  serialize_only = ('id', 'author_id', 'title', 'description', 'publish_date')

  id = db.Column(db.Integer, primary_key=True)
  author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), unique=False, nullable=False)
  title = db.Column(db.String(50))
  description = db.Column(db.String(200))
  publish_date = db.Column(db.DateTime())

  def __init__(self, author_id, title, description, publish_date):
    self.author_id = author_id
    self.title = title
    self.description = description
    self.publish_date = publish_date

  def __repr__(self):
    return '<id {}>'.format(self.id)
