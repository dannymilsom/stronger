from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model

from ..forms import LoginForm, UserForm

User = get_user_model()


def login(request):
    """Supports authentication for users."""

    data = {'login_form': LoginForm}
    authenticated = request.user.is_authenticated()

    if request.method == 'GET':
        # probably re-directed to /login via @login_required
        return render(request, "login.html", data)

    elif request.method == 'POST' and not authenticated:
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None and user.is_active:
            auth_login(request, user)
            authenticated = True

    # check the referer to see if we should redirect or send a JSON response
    if '/login' in request.META['HTTP_REFERER']:
        if authenticated:
            return HttpResponseRedirect(reverse('home'))
        else:
            data['authentication_error'] = True
            return render(request, "login.html", data)
    else:
        return JsonResponse({'authenticated': authenticated})

@login_required
def logout(request):
    """Logs a authenticated user out and redirects them to the homepage."""
    if request.user.is_authenticated():
        auth_logout(request)
        return HttpResponseRedirect(reverse('home'))

def signup(request):
    """Supports the creation of new user accounts."""

    data = {'signup_form': UserForm}

    if request.method == 'GET':
        # probably re-directed to /login via @login_required
        return render(request, "signup.html", data)

    registered = False
    authenticated = False

    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    if all((username, email, password)):
        user = User.objects.create_user(username, email, password)
        registered = True

        # authenticate them
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None and auth_user.is_active:
            auth_login(request, auth_user)
            authenticated = True

    # check the referer to see if we should redirect or send a JSON response
    if '/signup' in request.META['HTTP_REFERER']:
        if authenticated:
            return HttpResponseRedirect(reverse('home'))
        else:
            data['signup_error'] = True
            return render(request, "signup.html", data)
    else:
        return JsonResponse({
            'registered': registered,
            'authenticated': authenticated
        })
