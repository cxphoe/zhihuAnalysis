from models import Model
from db import Base

from sqlalchemy import Column, Integer, Unicode, UnicodeText, VARCHAR, ForeignKey, UniqueConstraint, Index

class User(Model, Base):
    __tablename__ = 'user'
    id = Column(VARCHAR(255), primary_key=True)
    name = Column(Unicode(50), default='')
    gender = Column(VARCHAR(10), default='')
    locations = Column(UnicodeText, default='')
    educations = Column(UnicodeText, default='')
    careers = Column(UnicodeText, default='')
    profession = Column(Unicode(50), default='')
    pins_count = Column(Integer, default=0)
    answer_count = Column(Integer, default=0)
    question_count = Column(Integer, default=0)
    articles_count = Column(Integer, default=0)
    followee_count = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    thanked_count = Column(Integer, default=0)
    thumbup_count = Column(Integer, default=0)
    favorited_count = Column(Integer, default=0)

