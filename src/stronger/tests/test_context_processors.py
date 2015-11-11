from django.core.urlresolvers import reverse
from django.test import TestCase

class ContextProcessorTest(TestCase):
    """
    Testing some custom context processors defined in context_processors.py.
    """

    def test_login_form(self):
        """
        Validate that the LoginForm form object is included in the 
        request context.
        """
        response = self.client.get(reverse('home'))
        self.assertIn('login_form', response.context)

    def test_signup_form(self):
        """
        Validate that the UserForm form objet is included in the 
        request context."""
        response = self.client.get(reverse('home'))
        self.assertIn('signup_form', response.context)

    def test_friend_form(self):
        """
        Validate that the FriendForm form objet is included in the 
        request context when the URL path starts with /user.
        """
        response = self.client.get(reverse('users'))
        self.assertIn('friend_form', response.context)

        response = self.client.get(reverse('home'))
        self.assertNotIn('friend_form', response.context)
