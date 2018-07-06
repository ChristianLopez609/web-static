import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	username = Column(String(50), nullable=False)
	email = Column(String(250), nullable=False)
	pw_hash = Column(String(250), nullable=False)

class Post(Base):
	__tablename__ = 'post'

	id = Column(Integer, primary_key=True)
	imagen = Column(String(50),nullable=False)
	titulo = Column(String(50),nullable=False)
	contenido = Column(String(250),nullable=False)
	url = Column(String(250),nullable=False)



engine = create_engine('sqlite:///primer_web.db')
Base.metadata.create_all(engine)