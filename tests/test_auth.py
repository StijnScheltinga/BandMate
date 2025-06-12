from fastapi import status
from app.config import settings
from datetime import datetime, timedelta
from jose import jwt

# Authorization headers are not relevant yet since user needs to be given them first through this endpoint

def test_token_valid_credentials(client, test_user):
	token_data = {
		"username": test_user["email"],
		"password": test_user["password"]
	}
	token_response = client.post("/auth/token", data=token_data)
	assert token_response.status_code == 200
	response = token_response.json()
	assert response["access_token"] != None
	assert response["refresh_token"] != None
	assert response["token_type"] != None

	# Test if the token grants access on protected endpoint
	access_token = response["access_token"]
	auth_header = {"Authorization": f"Bearer {access_token}"}
	response = client.get("/user/current", headers=auth_header)
	assert response.status_code == status.HTTP_200_OK

def test_token_incorrect_password(client, test_user):
	token_data = {
		"username": test_user["email"],
		"password": "incorrect password"
	}
	token_response = client.post("/auth/token", data=token_data)
	assert token_response.status_code == 401
	assert token_response.json() == {"detail": "Incorrect Password"}

def test_token_incorrect_username(client, test_user):
	token_data = {
		"username": "incorrect@gmail.com",
		"password": test_user["password"]
	}
	token_response = client.post("/auth/token", data=token_data)
	assert token_response.status_code == 404
	assert token_response.json() == {"detail": "Email not found"}

def test_refresh_valid_token(client, tokens):
	# Test endpoint
	refresh_token = tokens["refresh_token"]
	response = client.post('/auth/refresh', json=refresh_token)
	assert response.status_code == status.HTTP_200_OK
	response_json = response.json()
	assert response_json.get('access_token') is not None

	# Check if token grants acces to protected endpoint
	access_token = response_json["access_token"]
	auth_header = {"Authorization": f"Bearer {access_token}"}
	response = client.get("/user/current", headers=auth_header)
	assert response.status_code == status.HTTP_200_OK

def test_refresh_invalid_token(client):
	response = client.post('/auth/refresh', json="RandomStringNotAToken")
	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	assert response.json() == {"detail": "Invalid refresh token"}

# def test_refresh_expired_token(client, test_user):
# 	expired_token = jwt.encode(
# 		{
# 			"sub": test_user["email"],
# 			"exp": datetime.now(datetime.time)
# 		}
# 	)
