from fastapi import status
from app.models import User

def test_return_health_check(client):
	response = client.get('/health')
	assert response.status_code == status.HTTP_200_OK
	assert response.json() == {'status': 'Server is running'}
