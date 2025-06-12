from fastapi import status
import pytest

def test_get_all_genres(client_auth):
	response = client_auth.get("/genre/all")
	assert response.status_code == status.HTTP_200_OK

def test_get_all_genres_unauthorized(client):
	response = client.get("/genre/all")
	assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_genres(client_auth):
	response = client_auth.get("/genre/user")
	assert response.status_code == status.HTTP_200_OK

def test_get_user_genres_unauthorized(client):
	response = client.get("/genre/user")
	assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize(
    "client_fixture, payload, expected_status",
    [
        # Valid authorized request
        ("client_auth", {"genre_ids": [1, 4, 19]}, status.HTTP_200_OK),

        # Authorized request with an invalid genre ID
        ("client_auth", {"genre_ids": [1, 4, 19, -404]}, status.HTTP_404_NOT_FOUND),

        # Unauthorized request
        ("client", {"genre_ids": [1, 4, 19]}, status.HTTP_401_UNAUTHORIZED),

        # Authorized request with malformed data (validation error)
        ("client_auth", {"genre_ids": ["not_an_int"]}, status.HTTP_422_UNPROCESSABLE_ENTITY),

        # Authorized request with missing data (validation error)
        ("client_auth", {}, status.HTTP_422_UNPROCESSABLE_ENTITY),

		("client_auth", {"gerne_id": [5, 7]}, status.HTTP_422_UNPROCESSABLE_ENTITY)
    ]
)
def test_put_user_genres(client_fixture, payload, expected_status, request):
    client = request.getfixturevalue(client_fixture)
    response = client.put("/genre/user", json=payload)
    assert response.status_code == expected_status, response.json()