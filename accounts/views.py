from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
# from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from .graph_helper import get_user
from .auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token


def login(request):
    if request.user.is_authenticated:
        return redirect('interface:index')
    sign_in_url, state = get_sign_in_url()
    # Save the expected state so we can validate in the callback
    request.session['auth_state'] = state
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(sign_in_url)


def callback(request):
    expected_state = request.session.pop('auth_state', '')
    token = get_token_from_code(request.get_full_path(), expected_state)
    user = get_user(token)
    store_token(request, token)
    model_user = store_user(request, user)
    auth_login(request, model_user)
    return redirect('interface:index')


def logout(request):
    remove_user_and_token(request)
    auth_logout(request)
    return redirect('accounts:login')
