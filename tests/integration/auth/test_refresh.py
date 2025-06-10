from fastapi import status

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

def test_refresh_invalid(client):
	response = client.post('/auth/refresh', json="RandomStringNotAToken")
	assert response.status_code == status.HTTP_401_UNAUTHORIZED