from app.database import get_db
from app.models import Genre

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

def populate_initial_data():
	db = next(get_db())
	for genre_name in GENRES:
		if not db.query(Genre).filter(Genre.name == genre_name).first():
			db.add(Genre(name=genre_name))
	db.commit()