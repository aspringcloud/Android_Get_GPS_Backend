from requests_oauthlib import OAuth2Session
from .models import User
from django.conf import settings
import os
import time
import yaml


# This is necessary for testing with non-HTTPS localhost
# Remove this if deploying to production
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# This is necessary because Azure does not guarantee
# to return scopes in the same case and order as requested
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'

# Load the oauth_sign_info.yml file

accounts_stream = open('YMLdir/oauth_settings.yml', 'r')
sign_info = yaml.load(accounts_stream, yaml.SafeLoader)
authorize_url = '{0}{1}'.format(
    sign_info['authority'], sign_info['authorize_endpoint'])
token_url = '{0}{1}'.format(sign_info['authority'], sign_info['token_endpoint'])

# Method to generate a sign-in url


def get_sign_in_url():
  # Initialize the OAuth client
  aad_auth = OAuth2Session(sign_info['app_id'],
                           scope=sign_info['scopes'],
                           redirect_uri=sign_info['redirect'])

  sign_in_url, state = aad_auth.authorization_url(
      authorize_url, prompt='login')

  return sign_in_url, state

# Method to exchange auth code for access token


def get_token_from_code(callback_url, expected_state):
    # Initialize the OAuth client
    aad_auth = OAuth2Session(sign_info['app_id'],
                             state=expected_state,
                             scope=sign_info['scopes'],
                             redirect_uri=sign_info['redirect'])

    token = aad_auth.fetch_token(token_url,
                                 client_secret=sign_info['app_secret'],
                                 authorization_response=callback_url)

    return token

# def get_token(request):
#     token = request.session['oauth_token']
#     return token

def get_token(request):
    token = request.session['oauth_token']
    if token != None:
        # Check expiration
        now = time.time()
        # Subtract 5 minutes from expiration to account for clock skew
        expire_time = token['expires_at'] - 300
        if now >= expire_time:
            # Refresh the token
            aad_auth = OAuth2Session(sign_info['app_id'],
                                    token=token,
                                    scope=sign_info['scopes'],
                                    redirect_uri=sign_info['redirect'])

            refresh_params = {
                'client_id': sign_info['app_id'],
                'client_secret': sign_info['app_secret'],
            }
            new_token = aad_auth.refresh_token(token_url, **refresh_params)

            # Save new token
            store_token(request, new_token)

            # Return new access token
            return new_token

    else:
        # Token still valid, just return it
        return token


def store_token(request, token):
    
    # print(token)
    request.session['oauth_token'] = token


def store_user(request, user):
    try:
        model_user = User.objects.get(id__exact =  user['id'])
    except User.DoesNotExist as identifier:
        model_user = User()
        model_user.id = user['id']
        model_user.username = user['userPrincipalName']
        model_user.first_name = user['givenName']
        model_user.last_name = user['surname']
        model_user.email =  user['mail']
        model_user.displayName =  user['displayName']
        model_user.jobTitle =  user['jobTitle']
        model_user.mobilePhone =  user['mobilePhone']
        model_user.save()
    request.session['user'] = {
        'is_authenticated': True,
        'name': user['displayName'],
        'email': user['mail'] if (user['mail'] != None) else user['userPrincipalName']
    }
    return model_user




def remove_user_and_token(request):
    if 'oauth_token' in request.session:
        del request.session['oauth_token']
    if 'user' in request.session:
        del request.session['user']