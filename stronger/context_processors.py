from .forms import UserForm, FriendForm, LoginForm

def login_form(request):
    """
    Pass a authentication form to the template.
    """
    return {'login_form': LoginForm()}

def signup_form(request):
    """
    Pass a registraiton form to the template.
    """
    return {'signup_form': UserForm()}

def friend_form(request):
    if request.path.startswith('/user'):
        return {'friend_form': FriendForm()}
    else:
        return {}
