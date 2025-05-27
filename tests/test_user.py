from fastapi import status
from app.models import User

def test_create_user_valid(db_session, client):
	user_data = {
		"email": "user@gmail.com",
		"password": "Password123!"
	}
	response = client.post("/user/create_user", json=user_data)
	assert response.status_code == status.HTTP_201_CREATED
	assert response.json() == {"message": "succesfully created user"}

	user = db_session.query(User).filter_by(email=user_data["email"]).first()
	assert user != None
	assert user.email == user_data["email"]
	assert user.hashed_password != user_data["password"]

def test_create_user_wrong_email(db_session, client):
	user_data = {
		"email": "user.com",
		"password": "Password123!"
	}
	response = client.post("/user/create_user", json=user_data)
	assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_user_wrong_password(db_session, client):
	user_data = {
		"email": "user@gmail.com",
		"password": "password123"
	}
	response = client.post("/user/create_user", json=user_data)
	assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_current_user_valid_token(client, auth_headers):
	response = client.get('/user/current', headers=auth_headers)
	assert response.status_code == status.HTTP_200_OK

def test_current_user_no_token(client):
	response = client.get('/user/current')
	assert response.status_code == status.HTTP_401_UNAUTHORIZED