from fastapi import status

def test_location_complete_profile(client, user_with_profile, test_users):
	user_data = user_with_profile
	response = client.get('/filter/location', headers=user_data['auth_header'])
	assert response.status_code == status.HTTP_200_OK
	assert len(response.json()) == 10

def test_location_incomplete_profile(client, user_without_profile, test_users):
	user_data = user_without_profile
	response = client.get('/filter/location', headers=user_data['auth_header'])
	assert response.status_code == status.HTTP_400_BAD_REQUEST