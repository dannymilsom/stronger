"""Test all public facing views."""

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from stronger.models import Workout, DailyNutrition, Exercise

from .utils import (
    User,
    TEST_USERNAME,
    TEST_EMAIL,
    TEST_PASSWORD,
    TEST_CREDS,
    create_user,
)


class HomeTest(TestCase):
    """Tests for the website homepage."""

    def setUp(self):
        """Reverse match the homepage URL for re-use across tests."""
        self.home_url = reverse('home')

    def test_anonymous_users_can_view(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_home_template_used(self):
        response = self.client.get(self.home_url)
        self.assertTemplateUsed(response, 'home.html')


class AboutTest(TestCase):
    """Tests for the about page."""

    def setUp(self):
        """Reverse match the about URL for re-use across tests."""
        self.about_url = reverse('about')

    def test_anonymous_users_can_view(self):
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)

    def test_about_template_used(self):
        response = self.client.get(self.about_url)
        self.assertTemplateUsed(response, "about.html")


class LoginTest(TestCase):
    """Tests for the user authentication interface."""

    def setUp(self):
        """Initalize a basic user for use across all unit tests."""
        self.user = create_user()
        self.login_url = reverse('login')
        self.login_post_data = {
            'follow': True,
            'HTTP_REFERER': self.login_url,
        }

    def test_anonymous_users_can_view(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_about_template_used(self):
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, "login.html")

    def test_correct_credentials_authenticated(self):
        response = self.client.post(
            self.login_url,
            data=TEST_CREDS,
            **self.login_post_data
        )
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, reverse('home'))

    def test_incorrect_credentials_fails_authentication(self):
        response = self.client.post(
            self.login_url,
            data={
                'username': 'test-user',
                'password': 'wrong',
            },
            **self.login_post_data
        )
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")


class SignUpTest(TestCase):
    """Tests for the signup page which includes a registration form."""

    def setUp(self):
        """Create a basic user and common data for use across multiple tests."""
        self.signup_url = reverse('signup')
        self.signup_post_data = {
            'follow': True,
            'HTTP_REFERER': self.signup_url,
        }

    def test_anonymous_users_can_view(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)

    def test_about_template_used(self):
        response = self.client.get(self.signup_url)
        self.assertTemplateUsed(response, "signup.html")

    def test_signup_form_in_context(self):
        response = self.client.get(self.signup_url)
        self.assertIn('signup_form', response.context)

    def test_anonymous_user_can_register_new_account(self):
        response = self.client.post(
            self.signup_url,
            data={
                'username': TEST_USERNAME,
                'email': TEST_EMAIL,
                'password': TEST_PASSWORD,
            },
            **self.signup_post_data
        )
        self.assertIn('_auth_user_id', self.client.session)

        user = User.objects.get()
        self.assertEqual(user.username, TEST_USERNAME)
        self.assertEqual(user.email, TEST_EMAIL)

        self.assertRedirects(response, reverse('home'))

    def test_signup_form_validates_missing_username(self):
        response = self.client.post(
            self.signup_url,
            data={
                'email': TEST_EMAIL,
                'password': TEST_PASSWORD,
            },
            **self.signup_post_data
        )
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_form_validates_missing_email(self):
        response = self.client.post(
            self.signup_url,
            data={
                'username': TEST_USERNAME,
                'password': TEST_PASSWORD,
            },
            **self.signup_post_data
        )
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_form_validates_missing_password(self):
        response = self.client.post(
            self.signup_url,
            data={
                'username': TEST_USERNAME,
                'email': TEST_EMAIL,
            },
            **self.signup_post_data
        )
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertTemplateUsed(response, 'signup.html')


class DashboardTest(TestCase):
    """Tests for the dashboard page."""

    def setUp(self):
        """Create a basic user and common data for use across multiple tests."""
        self.user = create_user()
        self.dashboard_url = reverse('dashboard')

    def test_anonymous_users_cannot_view_and_redirected_to_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_anonymous_users_redirected_to_login(self):
        response = self.client.get(self.dashboard_url, follow=True)
        self.assertRedirects(
            response, '{}?next=/dashboard'.format(reverse('login'))
        )

    def test_authenticated_user_can_view(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_template_used(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(self.dashboard_url)
        self.assertTemplateUsed(response, 'dashboard_home.html')

    def test_context_data_included(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(self.dashboard_url)
        self.assertIn('news', response.context)
        self.assertIn('friends', response.context)
        self.assertIn('js_data', response.context)


class ProfileTest(TestCase):
    """Tests for the user profile page."""

    def setUp(self):
        """Create a basic user and common data for use across multiple tests."""
        self.user = create_user()

    def test_anonymous_users_cannot_view_and_redirected_to_login(self):
        response = self.client.get(reverse('profile',
            kwargs={'username': TEST_USERNAME}
        ))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_users_redirected_to_login(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': TEST_USERNAME}),
            follow=True
        )
        self.assertRedirects(
            response, '{}?next=/users/{}/'.format(
                reverse('login'), TEST_USERNAME
            )
        )

    def test_authenticated_user_can_view(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(
            reverse('profile', kwargs={'username': TEST_USERNAME})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_invalid_username_raises_404(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(
            reverse('profile', kwargs={'username': 'doesnotexist'}),
            follow=True,
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")


class SettingsTest(TestCase):
    """Tests for the user settings page."""

    def setUp(self):
        self.user = create_user()

    def test_settings_page_redirects_anonymous(self):
        response = self.client.post(reverse('settings'), follow=True)
        self.assertRedirects(response, "/login?next=/settings")

    def test_authenticated_users_can_access_settings(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "settings.html")
        self.assertIn('user_form', response.context)

    def test_authenticated_users_can_modify_settings(self):
        self.client.login(**TEST_CREDS)
        response = self.client.post(reverse('settings'),
                data={'gym': 'Bristol Gym'})
        self.assertEqual(response.context['user'].gym, 'Bristol Gym')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "settings.html")


class WorkoutsTest(TestCase):
    """Tests for the high level workouts page."""

    def setUp(self):
        self.user = create_user()

    def test_workouts_page_redirects_anonymous(self):
        response = self.client.get(reverse('workouts'), follow=True)
        self.assertRedirects(response, "/login?next=/workouts")
        response = self.client.post(reverse('workouts'), follow=True)
        self.assertRedirects(response, "/login?next=/workouts")

    def test_authenticated_users_can_access_workouts(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(reverse('workouts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "workouts.html")
        self.assertIn('workout_search', response.context)
        self.assertIn('workout_history', response.context)

    def test_workouts_redirects_to_workout_page_with_get_data(self):
        self.client.login(**TEST_CREDS)
        # we need to create a workout instance before we are re-directed to it
        wko = Workout.objects.create(user=self.user, date=timezone.now(),
                description='Bench day', comments='Good session with Ray')
        response = self.client.get(reverse('workouts'), {'name': wko.id},
                follow=True)
        self.assertRedirects(response, '/workouts/{}'.format(wko.id))
        self.assertTemplateUsed(response, "workout.html")


class WorkoutTest(TestCase):
    """Tests for the individual workout page."""

    def setUp(self):
        self.user = create_user()
        self.wko = Workout.objects.create(user=self.user, date=timezone.now(),
                description='Bench day', comments='Good session with Ray')

    def test_workout_page_redirects_anonymous(self):
        response = self.client.get(reverse('workout',
                kwargs={'workout_id': self.wko.id}), follow=True)
        self.assertRedirects(response, "/login?next=/workouts/{}".format(self.wko.id))
        response = self.client.post(reverse('workout',
                kwargs={'workout_id': self.wko.id}), follow=True)
        self.assertRedirects(response, "/login?next=/workouts/{}".format(self.wko.id))

    def test_authenticated_users_can_access_workout(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(reverse('workout',
                kwargs={'workout_id': self.wko.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "workout.html")

    def test_invalid_workout_raises_404(self):
        self.client.login(**TEST_CREDS)
        # 5 is an arbitary number
        self.assertRaises(Workout.DoesNotExist, Workout.objects.get, id=5)
        response = self.client.get(reverse('workout',
                kwargs={'workout_id': 5}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")


class RecordWorkoutTest(TestCase):

    def test_record_workout_page_redirects_anonymous(self):
        response = self.client.get(reverse('record_workout'), follow=True)
        self.assertRedirects(response, "/login?next=/record-workout")
        response = self.client.post(reverse('record_workout'), follow=True)
        self.assertRedirects(response, "/login?next=/record-workout")

    def test_authenticated_users_can_access_record_workouts_page(self):
        create_user()
        self.client.login(**TEST_CREDS)
        response = self.client.get(reverse('record_workout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "record_workout.html")
        self.assertIn('workout_form', response.context)
        self.assertIn('set_formset', response.context)

    def test_authenticated_users_can_record_workouts(self):
        """
        Help on testing django FormSets - stackoverflow.com/questions/1630754
        """
        create_user()
        self.client.login(**TEST_CREDS)
        response = self.client.post(reverse('record_workout'), data={
            'date': '2014-01-01',
            'description': 'Push session',
            'comments': 'Felt quite easy today',
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '',
        }, follow=True)
        self.assertRedirects(response, reverse('workout', kwargs={'workout_id':1}))


class TestNutrition(TestCase):

    def setUp(self):
        self.user = create_user()
        self.nutrition_data = {
            'user': self.user,
            'date': timezone.now().date().isoformat(),
            'calories': '3000',
            'protein': '150',
            'carbs': '140',
            'fats': '60',
            'created_on': timezone.now()
        }

    def test_nutrition_page_redirects_anonymous(self):
        response = self.client.get(reverse('nutrition'), follow=True)
        self.assertRedirects(response, "/login?next=/nutrition")
        response = self.client.post(reverse('nutrition'), follow=True)
        self.assertRedirects(response, "/login?next=/nutrition")

    def test_authenticated_users_can_access_nutrition_page(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(reverse('nutrition'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "nutrition.html")

    def test_authenticated_users_can_record_nutrition_details(self):
        self.client.login(**TEST_CREDS)
        response = self.client.post(reverse('nutrition'),
                data=self.nutrition_data, follow=True)
        self.assertRedirects(response, reverse('meal', kwargs={'meal_id': 1}))
        self.assertEqual(DailyNutrition.objects.all().count(), 1)


class TestExercises(TestCase):

    def setUp(self):
        self.user = create_user()
        self.exercise_data = {
            'name': 'Bench',
            'primary_muscle': 'Chest',
            'secondary_muscles': 'Triceps',
            'added_by': self.user,
        }

    def test_exercises_page_redirects_anonymous(self):
        response = self.client.get(reverse('exercises'), follow=True)
        self.assertRedirects(response, "/login?next=/exercises")
        response = self.client.post(reverse('exercises'), follow=True)
        self.assertRedirects(response, "/login?next=/exercises")

    def test_authenticated_users_can_access_exercises_page(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(reverse('exercises'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "exercises.html")

    def test_authenticated_users_can_create_exercises(self):
        self.client.login(**TEST_CREDS)
        response = self.client.post(reverse('exercises'),
                data=self.exercise_data, follow=True)
        self.assertEqual(Exercise.objects.all().count(), 1)
        self.assertRedirects(response, reverse('exercise',
                kwargs={'exercise_name': 'bench'}))
        self.assertTemplateUsed(response, "exercise.html")

    def test_authenticated_users_can_find_exercises(self):
        self.client.login(**TEST_CREDS)
        exc = Exercise.objects.create(**self.exercise_data)
        response = self.client.get(reverse('exercises'),
                data={'name': 'Bench'}, follow=True)
        self.assertRedirects(response, '/exercises/{}'.format(exc.clean_name))


class UsersTest(TestCase):

    def setUp(self):
        self.user = create_user()

    def test_users_page_redirects_anonymous(self):
        response = self.client.get(reverse('users'), follow=True)
        self.assertRedirects(response, '/login?next=/users/')

    def test_authenticated_users(self):
        self.client.login(**TEST_CREDS)
        response = self.client.get(reverse('users'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users.html")
