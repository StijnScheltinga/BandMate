import pytest
from app.models import Base
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base
from app.router.user import create_user
from fastapi.testclient import TestClient

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
	DATABASE_URL,
	connect_args={
		"check_same_thread": False,
	},
	poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
		"email": "test@example.com",
		"password": "Password123!"
	}
	response = client.post("/user/create_user", json=user_data)
	assert response.status_code == 201
	return user_data

@pytest.fixture(scope="session")
def access_token(client, test_user):
	token_data = {
		"username": test_user["email"],
		"password": test_user["password"]
	}
	token_response = client.post("/auth/token", data=token_data)
	assert token_response.status_code == 200
	return token_response.json()["access_token"]

@pytest.fixture
def auth_headers(access_token):
	return {"Authorization": f"Bearer {access_token}"}