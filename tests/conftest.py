import pytest
from app.models import Base, User
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base
from app.router.user import create_user
from fastapi.testclient import TestClient
from faker import Faker

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
	DATABASE_URL,
	connect_args={
		"check_same_thread": False,
	},
	poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

fake = Faker()

@pytest.fixture(autouse=True, scope="session")
def setup_and_teardown_db():
	Base.metadata.create_all(bind=engine)
	yield
	Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def db_session():
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()

@pytest.fixture(scope="session")
def client(db_session):
	def override_get_db():
		yield db_session

	app.dependency_overrides[get_db] = override_get_db
	client = TestClient(app)
	return client

@pytest.fixture(scope="session")
def test_user(client):
	user_data = {
		"email": "user@gmail.com",
		"password": "Password123!"
	}
	response = client.post("/user/create_user", json=user_data)
	assert response.status_code == 201
	return user_data

@pytest.fixture(scope="session")
def tokens(client, test_user):
	token_data = {
		"username": test_user["email"],
		"password": test_user["password"]
	}
	response = client.post("/auth/token", data=token_data)
	assert response.status_code == 200
	return response.json()

@pytest.fixture
def auth_headers(tokens):
	access_token = tokens["access_token"]
	return {"Authorization": f"Bearer {access_token}"}

def create_test_user(client, email=None, password=None):
	user_data = {
		"email": email or fake.email(),
		"password": password or "Password123!"
	}
	response = client.post("/user/create_user", json=user_data)
	assert response.status_code == 201
	return user_data

def authenticate(client, user_data):
	token_response = client.post("/auth/token", data={
		"username": user_data["email"],
		"password": user_data["password"]
	})
	assert token_response.status_code == 200
	token = token_response.json()["access_token"]
	auth_header = {"Authorization": f"Bearer {token}"}
	return auth_header


@pytest.fixture(scope="session")
def user_without_profile(client):
	user_data = create_test_user(client, "user2@gmail.com")
	auth_header = authenticate(client, user_data)
	return {
		"user": user_data,
		"auth_header": auth_header
	}

@pytest.fixture(scope="session")
def user_with_profile(client):
	user_data = create_test_user(client, "user3@gmail.com")
	auth_header = authenticate(client, user_data)

	# Set up profile
	profile_data = {
		"display_name": fake.user_name(),
		"genre_ids": [1, 3],
		"instrument_ids": [4, 6],
		"latitude": float(fake.latitude()),
		"longitude": float(fake.longitude())
	}
	profile_response = client.post("/profile/setup", headers=auth_header, json=profile_data)
	assert profile_response.status_code == 201

	return {
		"user": user_data,
		"auth_header": auth_header,
		"profile": profile_data
	}

@pytest.fixture
def test_users(db_session):
	users = []
	for x in range(10):
		user = User(
			email=fake.email(),
			hashed_password=fake.password(),
			display_name=fake.user_name(),
			latitude=fake.latitude(),
			longitude=fake.longitude()
		)
		db_session.add(user)
		users.append(user)
	db_session.commit()
	yield users
	for user in users:
		db_session.delete(user)
	db_session.commit()
