from django.http.response import JsonResponse
import jwt
from rest_framework import authentication, exceptions, status
# from account.models import *
from Crm_app.models import CustomUser
from django.conf import settings
from rest_framework.response import Response
from jose.constants import ALGORITHMS
from datetime import datetime, timedelta
from django.conf import settings
import jwt


def generate_token(user_data):
    user_id = user_data.id  # Assuming the user_data object has the CustomUser instance
    auth_token = jwt.encode(
        {'user_id': user_id, 'name': user_data.username, 'exp': datetime.utcnow() + timedelta(days=1)},
        str(settings.JWT_SECRET_KEY), algorithm="HS256")
    return {
        'token': auth_token,
        'expires': datetime.utcnow() + timedelta(days=1)
    }


def authorization_required(func):
    def checkAuthData(request, *args, **kwargs):
        try:
            if 'Authorization' in request.headers and request.headers['Authorization']:
                auth_data = request.headers['Authorization']
            else:
                return JsonResponse({'error': {'code': 'AUTHENTICATION_FAILURE',
                                               'message': 'You are not authorized to perform this operation.'}},
                                    status=status.HTTP_401_UNAUTHORIZED)

            if "Bearer " not in auth_data:
                return JsonResponse({'error': {'code': 'INVALID_TOKEN_FORMAT', 'message': 'Check the token format.'}},
                                    status=status.HTTP_401_UNAUTHORIZED)

            auth_data = auth_data.split(' ')[1]

        except IndexError as e:
            return JsonResponse({'error': {'message': str(e)}}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = request.user  # Assuming request.user contains the authenticated CustomUser instance
            user_id = user.id
        except AttributeError:
            return JsonResponse({'error': {"code": "USER_NOT_AUTHENTICATED", 'message': 'User is not authenticated.'}},
                                status=status.HTTP_401_UNAUTHORIZED)

        return func(request, *args, **kwargs)

    return checkAuthData