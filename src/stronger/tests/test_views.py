from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from stronger.models import Workout, DailyNutrition, Exercise

User = get_user_model()

# http://stackoverflow.com/questions/11885211/
# https://github.com/toastdriven/guide-to-testing-in-django/blob/master/polls/tests/views.py

test_username = 'test-user'
test_email = 'test@example.com'
test_password = 'testing'
test_creds = {
    'username': test_username,
    'password': test_password
}

def create_test_user():
    """
    A utility function we can use in multiple TestCase classes to reduce DRY.
    """
    return User.objects.create_user(test_username, test_email, test_password)


class HomeTest(TestCase):

    def test_homepage_template_is_rendered(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


class AboutTest(TestCase):

    def test_about_template_is_rendered(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")


class LoginTest(TestCase):

    def setUp(self):
        self.user = create_test_user()

    def test_login_template_is_rendered(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_users_can_login(self):
        response = self.client.post(reverse('login'),
                data=test_creds, follow=True, HTTP_REFERER=reverse('login'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, reverse('home'))

    def test_wrong_details_fail_authentication(self):
        response = self.client.post(reverse('login'),
                data={'username': 'test-user', 'password': 'wrong'},
                follow=True, HTTP_REFERER=reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")


class SignUpTest(TestCase):

    def test_signup_template_is_rendered_with_signup_form(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertIn('signup_form', response.context)

    def test_users_can_signup(self):
        response = self.client.post(reverse('signup'),
                data={
                    'username': test_username,
                    'email': test_email,
                    'password': test_password,
                }, follow=True, HTTP_REFERER=reverse('signup'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertRedirects(response, reverse('home'))

    def test_signup_form_flags_missing_username(self):
        response = self.client.post(reverse('signup'),
                data={
                    'email': test_email,
                    'password': test_password,
                }, HTTP_REFERER=reverse('signup'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_form_flags_missing_email(self):
        response = self.client.post(reverse('signup'),
                data={
                    'username': test_username,
                    'password': test_password,
                }, HTTP_REFERER=reverse('signup'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_form_flags_missing_password(self):
        response = self.client.post(reverse('signup'),
                data={
                    'username': test_username,
                    'email': test_email,
                }, HTTP_REFERER=reverse('signup'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertTemplateUsed(response, 'signup.html')


class DashboardTest(TestCase):

    def test_dashboard_redirects_anonymous(self):
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertRedirects(response, '/login?next=/dashboard')

    def test_dashboard(self):
        create_test_user()
        self.client.login(username=test_username, password=test_password)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard_home.html")
        self.assertIn('news', response.context)
        self.assertIn('friends', response.context)
        self.assertIn('js_data', response.context)


class ProfileTest(TestCase):

    def test_profile_redirects_anonymous(self):
        response = self.client.get(reverse('profile',
                kwargs={'username': test_username}), follow=True)
        self.assertRedirects(response, '/login?next=/users/test-user/')

    def test_authenticated_user_can_view_profile(self):
        create_test_user()
        self.client.login(**test_creds)
        response = self.client.get(reverse('profile',
                kwargs={'username': test_username}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_invalid_username_raises_404(self):
        create_test_user()
        self.client.login(**test_creds)
        response = self.client.get(reverse('profile',
                kwargs={'username': 'fake'}), follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")


class SettingsTest(TestCase):

    def setUp(self):
        self.user = create_test_user()

    def test_settings_page_redirects_anonymous(self):
        response = self.client.get(reverse('settings'), follow=True)
        self.assertRedirects(response, "/login?next=/settings")
        response = self.client.post(reverse('settings'), follow=True)
        self.assertRedirects(response, "/login?next=/settings")

    def test_authenticated_users_can_access_settings(self):
        self.client.login(**test_creds)
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "settings.html")
        self.assertIn('user_form', response.context)

    def test_authenticated_users_can_modify_settings(self):
        self.client.login(**test_creds)
        response = self.client.post(reverse('settings'),
                data={'gym': 'Bristol Gym'})
        self.assertEqual(response.context['user'].gym, 'Bristol Gym')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "settings.html")


class WorkoutsTest(TestCase):

    def setUp(self):
        self.user = create_test_user()

    def test_workouts_page_redirects_anonymous(self):
        response = self.client.get(reverse('workouts'), follow=True)
        self.assertRedirects(response, "/login?next=/workouts")
        response = self.client.post(reverse('workouts'), follow=True)
        self.assertRedirects(response, "/login?next=/workouts")

    def test_authenticated_users_can_access_workouts(self):
        self.client.login(**test_creds)
        response = self.client.get(reverse('workouts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "workouts.html")
        self.assertIn('workout_search', response.context)
        self.assertIn('workout_history', response.context)

    def test_workouts_redirects_to_workout_page_with_get_data(self):
        self.client.login(**test_creds)
        # we need to create a workout instance before we are re-directed to it
        wko = Workout.objects.create(user=self.user, date=timezone.now(),
                description='Bench day', comments='Good session with Ray')
        response = self.client.get(reverse('workouts'), {'name': wko.id},
                follow=True)
        self.assertRedirects(response, '/workouts/{}'.format(wko.id))
        self.assertTemplateUsed(response, "workout.html")


class WorkoutTest(TestCase):

    def setUp(self):
        self.user = create_test_user()
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
        self.client.login(**test_creds)
        response = self.client.get(reverse('workout',
                kwargs={'workout_id': self.wko.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "workout.html")

    def test_invalid_workout_raises_404(self):
        self.client.login(**test_creds)
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
        create_test_user()
        self.client.login(**test_creds)
        response = self.client.get(reverse('record_workout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "record_workout.html")
        self.assertIn('workout_form', response.context)
        self.assertIn('set_formset', response.context)

    def test_authenticated_users_can_record_workouts(self):
        """
        Help on testing django FormSets - stackoverflow.com/questions/1630754
        """
        create_test_user()
        self.client.login(**test_creds)
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
        self.user = create_test_user()
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
        self.client.login(**test_creds)
        response = self.client.get(reverse('nutrition'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "nutrition.html")

    def test_authenticated_users_can_record_nutrition_details(self):
        self.client.login(**test_creds)
        response = self.client.post(reverse('nutrition'),
                data=self.nutrition_data, follow=True)
        self.assertRedirects(response, reverse('meal', kwargs={'meal_id': 1}))
        self.assertEqual(DailyNutrition.objects.all().count(), 1)


class TestExercises(TestCase):

    def setUp(self):
        self.user = create_test_user()
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
        self.client.login(**test_creds)
        response = self.client.get(reverse('exercises'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "exercises.html")

    def test_authenticated_users_can_create_exercises(self):
        self.client.login(**test_creds)
        response = self.client.post(reverse('exercises'),
                data=self.exercise_data, follow=True)
        self.assertEqual(Exercise.objects.all().count(), 1)
        self.assertRedirects(response, reverse('exercise',
                kwargs={'exercise_name': 'bench'}))
        self.assertTemplateUsed(response, "exercise.html")

    def test_authenticated_users_can_find_exercises(self):
        self.client.login(**test_creds)
        exc = Exercise.objects.create(**self.exercise_data)
        response = self.client.get(reverse('exercises'),
                data={'name': 'Bench'}, follow=True)
        self.assertRedirects(response, '/exercises/{}'.format(exc.clean_name))


class UsersTest(TestCase):

    def setUp(self):
        self.user = create_test_user()

    def test_users_page_redirects_anonymous(self):
        response = self.client.get(reverse('users'), follow=True)
        self.assertRedirects(response, '/login?next=/users/')

    def test_authenticated_users(self):
        self.client.login(**test_creds)
        response = self.client.get(reverse('users'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users.html")

