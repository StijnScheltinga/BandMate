from app.database import Base
from sqlalchemy import Table, Column, Integer, String, Float, Boolean, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

# Joining Tables
user_band = Table(
	'user_band', 
	Base.metadata, 
	Column('user_id', Integer, ForeignKey('user.id')),
	Column('band_id', Integer, ForeignKey('band.id')),
	UniqueConstraint('user_id', 'band_id')
)

user_genre = Table(
	'user_genre', 
	Base.metadata, 
	Column('user_id', Integer, ForeignKey('user.id')),
	Column('genre_id', Integer, ForeignKey('genre.id')),
	UniqueConstraint('user_id', 'genre_id')
)

user_instrument = Table(
	'user_instrument',
	Base.metadata,
	Column('user_id', Integer, ForeignKey('user.id')),
	Column('instrument_id', Integer, ForeignKey('instrument.id')),
	UniqueConstraint('user_id', 'instrument_id')
)

band_genre = Table(
	'band_genre', 
	Base.metadata, 
	Column('band_id', Integer, ForeignKey('band.id')),
	Column('genre_id', Integer, ForeignKey('genre.id')),
	UniqueConstraint('band_id', 'genre_id')
)

# An user has 1 city, 0/many bands, 0/many genres.
class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)

	email = Column(String(255), unique=True, nullable=False)
	hashed_password = Column(String(255), nullable=False)

	display_name = Column(String(255), nullable=True)
	latitude = Column(Float, nullable=True)
	longitude = Column(Float, nullable=True)
	refresh_token = Column(String(255), nullable=True)
	profile_picture = Column(String(255), nullable=True)
	city = Column(String(255), nullable=True)

	setup_complete = Column(Boolean, default=False, nullable=False)

	bands = relationship('Band', secondary=user_band, back_populates='users')
	genres = relationship('Genre', secondary=user_genre, back_populates='users')
	instruments = relationship('Instrument', secondary=user_instrument, back_populates='users')
	media = relationship('Media', back_populates='user', cascade='all, delete-orphan')
	outgoing_invites = relationship('BandInvite', foreign_keys='[BandInvite.sender_id]', back_populates='sender', cascade='all, delete-orphan')
	incoming_invites = relationship('BandInvite', foreign_keys='[BandInvite.reciever_id]', back_populates='reciever', cascade='all, delete-orphan')

class Band(Base):
	__tablename__ = 'band'

	id = Column(Integer, primary_key=True)
	name = Column(String(255))

	# For many to many arguments are class name, joining table and the attribute
	users = relationship('User', secondary=user_band, back_populates='bands')
	genres = relationship('Genre', secondary=band_genre, back_populates='bands')
	invites = relationship('BandInvite', back_populates='band', cascade='all, delete-orphan')

class Genre(Base):
	__tablename__ = 'genre'

	id = Column(Integer, primary_key=True)
	name = Column(String(255))

	users = relationship("User", secondary=user_genre, back_populates='genres')
	bands = relationship("Band", secondary=band_genre, back_populates='genres')

class Instrument(Base):
	__tablename__ = 'instrument'

	id = Column(Integer, primary_key=True)
	name = Column(String(255))

	users = relationship('User', secondary=user_instrument, back_populates='instruments')

class Media(Base):
	__tablename__ = 'media'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('user.id'))
	blob_url = Column(String, nullable=False)

	user = relationship('User', back_populates='media')

class BandInvite(Base):
	__tablename__ = "band_invite"

	id = Column(Integer, primary_key=True)
	band_id = Column(Integer, ForeignKey('band.id'))
	sender_id = Column(Integer, ForeignKey('user.id'))
	reciever_id = Column(Integer, ForeignKey('user.id'))
	status = Column(Enum("pending", "accepted", "declined", name="status"), default="pending")

	band = relationship("Band", foreign_keys=band_id, back_populates='invites')
	sender = relationship("User", foreign_keys=sender_id, back_populates='outgoing_invites')
	reciever = relationship("User", foreign_keys=reciever_id, back_populates='incoming_invites')

	__table_args__ = (UniqueConstraint("sender_id", "reciever_id", "band_id", name="unique_band_invite"),)


