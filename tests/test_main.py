from fastapi import status
from app.models import User

'''
naming convention for the test functions:
test_{endpoint name}_{type test}
'''

def test_health(client):
	response = client.get('/health')
	assert response.status_code == status.HTTP_200_OK
	assert response.json() == {'status': 'Server is running'}
