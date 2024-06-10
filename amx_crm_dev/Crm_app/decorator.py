from rest_framework.response import Response
import jwt
from rest_framework import authentication, exceptions, status
from django.conf import settings
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from jose import jwt


def AutorizationRequired(func):
    def checkAuthData(request, *args, **kwargs):
        try:
            if ('Authorization' in request.headers) and (len(request.headers['Authorization']) != 0):
                pass
            else:
                # raise exceptions.AuthenticationFailed(
                #     {'error': {'code': 'AUTHENTICATION_FAILURE', 'message': 'You are not authorized to perform this operation. '}})
                # return render(request, 'error-page.html', status=status.HTTP_401_UNAUTHORIZED)
                return JsonResponse({'error': {'code': 'AUTHENTICATION_FAILURE',
                                               'message': 'You are not authorized to perform this operation. '}},
                                    status=status.HTTP_401_UNAUTHORIZED)

            auth_data = request.headers['Authorization']
            if not auth_data:
                return JsonResponse(
                    {'error': {'code': 'INVALID_HEADER_FORMAT', 'message': 'you must be passed as Auth header '}},
                    status=status.HTTP_401_UNAUTHORIZED)
            if "Bearer " not in auth_data:
                return JsonResponse(
                    {'error': {'code': 'INVALID_TOKEN_FORMAT', 'message': 'check the token format '}},
                    status=status.HTTP_401_UNAUTHORIZED)
            auth_data = auth_data.split(' ')[1]

        except IndexError as e:
            return Response({'error': {'message': e}})

        try:
            print(settings.JWT_SECRET_KEY, '==========secret-key===========')
            payload = jwt.decode(auth_data, str(
                settings.JWT_SECRET_KEY), algorithms="HS256")
            # payload_id = payload['user_id']
            # print("payload_id",payload_id)
            # user_id = CustomUser.objects.get(id=payload_id)
            # return user_id

        except jwt.DecodeError as identifier:
            return JsonResponse({'error': {"code": "AUTHENTICATION_FAILURE", 'message': 'You token is not valid'}},
                                status=status.HTTP_401_UNAUTHORIZED)
        except jwt.ExpiredSignatureError as identifier:
            return JsonResponse(
                {'error': {"code": "AUTHENTICATION_FAILURE", 'message': 'token expired!,enter valid token'}},
                status=status.HTTP_401_UNAUTHORIZED)
        return func(request, *args, **kwargs)

    return checkAuthData