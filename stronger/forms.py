from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
User = get_user_model()

from stronger.models import (Friend, Group, Workout, Set, Exercise, 
                            BodyWeight, DailyNutrition)


class UserForm(forms.ModelForm):

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Username',
        'class': 'wide-form-field',
        'title': 'Please enter a username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'wide-form-field',
        'title': 'Please enter a password'
    }))
    email = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Email',
        'class': 'wide-form-field',
        'title': 'Please enter a email address'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('gravatar', 'gym', 'goals', 'about')
        widgets = {
            'gravatar': forms.TextInput(attrs={
                'placeholder': 'www.mywebsite.com/myimage.jpg',
                'class': 'col-xs-12 col-sm-offset-2 col-sm-8 bottom-buffer',
                'title': 'Gravatar URL'
            }),
            'gym': forms.TextInput(attrs={
                'placeholder': 'Gym',
                'class': 'col-xs-12 col-sm-offset-2 col-sm-8 bottom-buffer',
                'title': 'Gym'
            }),
            'goals': forms.Select(attrs={
                'class': 'col-xs-12 col-sm-offset-2 col-sm-8 bottom-buffer',
                'placeholder': 'Goals',
                'title': 'Goals'
            }),
            'about': forms.Textarea(attrs={
                'placeholder': 'Been training for 4 year...',
                'class': 'col-xs-12 col-sm-offset-2 col-sm-8 bottom-buffer',
                'title': 'About you...', 'rows': 2
            }),
        }

class FindUserForm(forms.ModelForm):
    """
    Provides users a select list of registered users.
    """

    username = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        empty_label="Find a user",
        widget=forms.Select(attrs={
            'title': 'Find a user'
            })
    )

    class Meta:
        model = User
        fields = ('username',)

class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Username',
        'class': 'wide-form-field',
        'title': 'Please enter your username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'wide-form-field',
        'title': 'Please enter your password'
    }))

class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ('name', 'about')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Group Name',
                'class': 'wide-form-field'
            }),
            'about': forms.TextInput(attrs={
                'placeholder': 'Description',
                'class': 'wide-form-field'
            })
        }

class FriendForm(forms.ModelForm):
    friend = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = Friend
        fields = ('friend',)

class AddFriendForm(forms.ModelForm):

    class Meta:
        model = Friend
        fields = ('user', 'friend')

class Html5DateInput(forms.DateInput):
    """
    Changes input type to support browser default datepicker rendering. This is 
    part of the HTML5 API, so we still load jQuery UI and the DatePicker JS 
    if the browser doesn't support this feature yet (cough firefox cough).
    """
    input_type = 'date'

class WorkoutForm(forms.ModelForm):

    class Meta:
        model = Workout
        fields = ('date', 'description', 'comments')
        widgets = {
            'date': Html5DateInput(),
            'date': forms.TextInput(attrs={
                'placeholder': '2014-06-30',
                'class': 'workout-meta col-xs-12',
                'title': 'Date of the workout'
            }),
            'description': forms.TextInput(attrs={
                'placeholder': 'Shoulder + Tris',
                     'class': 'workout-meta col-xs-12',
                     'title': 'Name of the workout'
            }),
            'comments': forms.Textarea(attrs={
                'placeholder': 'Good session today with Des',
                  'class': 'workout-meta col-xs-12',
                  'title': 'Additional comments',
                  'rows': 2
            }),
        }

class EditWorkoutForm(forms.ModelForm):

    class Meta:
        model = Workout
        fields = ('date', 'description', 'comments')
        widgets = {
            'date': Html5DateInput(),
            'date': forms.TextInput(attrs={
                'placeholder': '2014-06-30',
                'class': 'workout-date wide-form-field',
                'title': 'Date of the workout'
            }),
            'description': forms.TextInput(attrs={
                'placeholder': 'Shoulder + Tris',
                      'class': 'workout-description wide-form-field',
                      'title': 'Name of the workout'
            }),
            'comments': forms.Textarea(attrs={
                'placeholder': 'Good session today with Des',
                  'class': 'workout-comments form-field col-xs-12',
                  'title': 'Additional comments',
                  'rows': 2
            }),
        }


class SetForm(forms.ModelForm):

    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.all(),
        empty_label="Pick an exercise",
        widget=forms.Select(attrs={
            'class': 'workout-exercise col-xs-12',
            'title': 'Select an exercise'
        })
    )

    class Meta:
        model = Set
        fields = ('exercise', 'weight', 'reps')
        widgets = {
            'weight': forms.TextInput(attrs={
                'placeholder': '60kg',
                'class': 'col-xs-6 weight'
            }),
            'reps': forms.TextInput(attrs={
                'placeholder': '10',
                'class': 'col-xs-6 reps'
            }),
        }

class FindWorkoutForm(forms.ModelForm):
    """
    Rendersa select list, from which users can pick a workout they have 
    previously recorded.
    """

    def __init__(self, user, *args, **kwargs):
        super(FindWorkoutForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.ModelChoiceField(
            queryset=Workout.objects.filter(user=user)
        )

    name = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'wide-form-field',
        'title': 'Find a Workout'
    }))

    class Meta:
        model = Exercise
        fields = ('name',)

class AddExerciseForm(forms.ModelForm):
    """
    Provides a user friendly way to create a new Exercise object.
    """

    class Meta:
        model = Exercise
        fields = ('name', 'primary_muscle', 'secondary_muscles')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Exercise Name',
                'class': 'wide-form-field grey-round-border'
            }),
            'primary_muscle': forms.Select(attrs={
                'class': 'wide-form-field'
            }),
            'secondary_muscles': forms.Select(attrs={
                'class': 'wide-form-field'
            }),
        }

class FindExerciseForm(forms.ModelForm):
    """
    Provides users a select list, from which they can choose an exercise.
    """

    name = forms.ChoiceField(widget=forms.Select(attrs={
        'class': 'wide-form-field',
        'title': 'Find an Exercise'
    }), choices=Exercise.objects.categorise_exercises())

    class Meta:
        model = User
        fields = ('name',)

class ExerciseProgressForm(forms.ModelForm):

    name = forms.ModelChoiceField(queryset=Exercise.objects.all())

    class Meta:
        model = Exercise
        fields = ('name',)

class BodyWeightForm(forms.ModelForm):

    bodyweight = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Bodyweight (KG)',
        'class': 'wide-form-field'
    }))
    date = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Date (YYYY-MM-DD)',
        'class': 'wide-form-field'
    }))

    class Meta:
        model = BodyWeight
        fields = ('bodyweight', 'date')

class DailyNutritionForm(forms.ModelForm):

    class Meta:
        model = DailyNutrition
        fields = ('date', 'calories', 'protein', 'carbs', 'fats')
        widgets = {
            'date': Html5DateInput(),
            'calories': forms.TextInput(attrs={
                'placeholder': 'Calories',
                'class': 'wide-form-field'
            }),
            'protein': forms.TextInput(attrs={
                'placeholder': 'Protein',
                'class': 'wide-form-field'
            }),
            'carbs': forms.TextInput(attrs={
                'placeholder': 'Carbs',
                'class': 'wide-form-field'
            }),
            'fats': forms.TextInput(attrs={
                'placeholder': 'Fats',
                'class': 'wide-form-field'
            }),
        }

