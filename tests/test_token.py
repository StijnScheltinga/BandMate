from fastapi import status

# Test happy flow for token endpoint
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
	assert token_response.json() == {"detail": "User not found"}