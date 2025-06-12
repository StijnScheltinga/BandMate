from app.database import get_db
from app.models import Genre, Instrument

GENRES = [
    "Blues",
    "Classical",
    "Country",
    "Disco",
    "Electronic",
    "Folk",
    "Funk",
    "Hip Hop",
    "Indie",
    "Jazz",
    "K-Pop",
    "Latin",
    "Metal",
    "Pop",
    "Punk",
    "R&B",
    "Rap",
    "Reggae",
    "Rock",
    "Soul"
]

INSTRUMENTS = [
    "Acoustic Guitar",
    "Electric Guitar",
    "Bass Guitar",
    "Drums",
    "Piano",
    "Keyboard",
    "Violin",
    "Cello",
    "Trumpet",
    "Saxophone",
    "Flute",
    "Clarinet",
    "Trombone",
    "Harmonica",
    "Ukulele",
    "Banjo",
    "Synthesizer",
    "DJ Controller",
    "Percussion",
    "Vocals"
]

def populate_initial_data(g_db):

	db = next(g_db())
	for genre_name in GENRES:
		if not db.query(Genre).filter(Genre.name == genre_name).first():
			db.add(Genre(name=genre_name))

	for instrument_name in INSTRUMENTS:
		if not db.query(Instrument).filter(Instrument.name == instrument_name).first():
			db.add(Instrument(name=instrument_name))

	db.commit()