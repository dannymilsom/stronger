"""Utility methods we can reuse across various test cases."""

from django.contrib.auth import get_user_model


User = get_user_model()

TEST_USERNAME = 'test-user'
TEST_EMAIL = 'test@example.com'
TEST_PASSWORD = 'testing'

TEST_CREDS = {
    'username': TEST_USERNAME,
    'password': TEST_PASSWORD
}

def create_user(username=TEST_USERNAME, email=TEST_EMAIL, password=TEST_PASSWORD):
    """Create a simple test user with the minimal attributes required."""
    return User.objects.create_user(username, email, password)
