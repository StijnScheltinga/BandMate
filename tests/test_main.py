from fastapi import status
from app.models import User
from app.router.auth import authenticate_user

def test_return_health_check(client):
	response = client.get('/health')
	assert response.status_code == status.HTTP_200_OK
	assert response.json() == {'status': 'Server is running'}

def test_create_user(db_session, client):
	user_data = {
		"email": "user@gmail.com",
		"password": "password123"
	}
	response = client.post("/auth/create_user", json=user_data)
	assert response.status_code == status.HTTP_201_CREATED
	assert response.json() == None

	user = db_session.query(User).filter_by(email=user_data["email"]).first()
	assert user != None
	assert user.email == user_data["email"]
	assert user.hashed_password != user_data["password"]

def test_current_user(client, auth_headers):
	response = client.get('/user/current', headers=auth_headers)
	assert response.status_code == status.HTTP_200_OK

	response = client.get('/user/current')
	assert response.status_code == status.HTTP_401_UNAUTHORIZED