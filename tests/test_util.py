from app.util.location import haversine, get_city_from_latlong

def test_haversine_london_to_amsterdam():
	distance = haversine(51.50696757084134, -0.11056107743527625, 52.37389462821479, 4.895185930281781)
	assert int(distance) >= 355 and int(distance) <= 357

def test_haversine_amsterdam_to_new_york( ):
	distance = haversine(52.37389462821479, 4.895185930281781, 40.7696532657234, -73.97433781915613)
	assert int(distance) >= 5850 and int(distance) <= 5860

def test_get_city_from_latlong():
	# pin in Amsterdam
	assert get_city_from_latlong(52.37311571170095, 4.894771408476586) == "Amsterdam"
	# pin in Risdam, Zwaag
	assert get_city_from_latlong(52.6644644312896, 5.051730851294935) == "Zwaag"
	#pin in Risdam, Hoorn
	assert get_city_from_latlong(52.659298942395175, 5.0487866981365475) == "Hoorn"
	#pin in North Sea
	assert get_city_from_latlong(56.46658546172746, 3.465524410338841) is None
	#pin in western sahara
	assert get_city_from_latlong(22.786587242597186, -14.591998895748688) is None