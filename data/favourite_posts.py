import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class FavouritePosts(SqlAlchemyBase):
    __tablename__ = 'favourite_posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    post_id = sqlalchemy.Column(sqlalchemy.Integer)
    author_id = sqlalchemy.Column(sqlalchemy.Integer)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.String)
    tags = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author_name = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    key = sqlalchemy.Column(sqlalchemy.Integer,
                            sqlalchemy.ForeignKey("users.id"))
