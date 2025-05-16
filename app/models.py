from app.database import Base
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Joining Tables
user_band = Table(
	'user_band', 
	Base.metadata, 
	Column('user_id', Integer, ForeignKey('user.id')),
	Column('band_id', Integer, ForeignKey('band.id'))
)

band_genre = Table(
	'band_genre', 
	Base.metadata, 
	Column('band_id', Integer, ForeignKey('band.id')),
	Column('genre_id', Integer, ForeignKey('genre.id'))
)

user_genre = Table(
	'user_genre', 
	Base.metadata, 
	Column('user_id', Integer, ForeignKey('user.id')),
	Column('genre_id', Integer, ForeignKey('genre.id'))
)

# An user had 1 city, 0/many bands, 0/many genres.
class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	email = Column(String(255), unique=True)
	hashed_password = Column(String(255))
	display_name = Column(String(255))
	city_id = Column(Integer, ForeignKey('city.id')) # "city.id" must match tablename

	city = relationship('City', back_populates='users')
	bands = relationship('Band', secondary=user_band, back_populates='users')
	genres = relationship('Genre', secondary=user_genre, back_populates='users')


class City(Base):
	__tablename__ = 'city'

	id = Column(Integer, primary_key=True)
	city_name = Column(String)

	#can filter users linked to a city
	users = relationship('User', back_populates='city')


class Band(Base):
	__tablename__ = 'band'

	id = Column(Integer, primary_key=True)
	name = Column(String(255))

	# For many to many arguments are class name, joining table and the attribute
	users = relationship('User', secondary=user_band, back_populates='bands')
	genres = relationship('Genre', secondary=band_genre, back_populates='bands')

class Genre(Base):
	__tablename__ = 'genre'

	id = Column(Integer, primary_key=True)
	name = Column(String(255))

	users = relationship("User", secondary=user_genre, back_populates='genres')
	bands = relationship("Band", secondary=band_genre, back_populates='genres')