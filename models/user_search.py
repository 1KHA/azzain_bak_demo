from datetime import datetime
from database import db, ma
from marshmallow import fields


class UserSearch(db.Model):
    """
        User Search History table about the products
    """
    __tablename__ = 'user_searches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    search_query = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
