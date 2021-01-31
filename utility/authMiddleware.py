import jwt
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from config.configConstants import JWTConstants
from config.messages import Messages
from auth_user.models import (User,Device)


# This function is used to authenticate after login
def isAuthenticate(function):
    def wrap(request, *args, **kwargs):
        try:
            if request.META.get('HTTP_AUTHORIZATION') and request.META.get('HTTP_AUTHORIZATION') != 'invalidtoken':
                token = request.META.get('HTTP_AUTHORIZATION')
                # validating access token
                try:
                    # Decode payload
                    payload = jwt.decode(token, JWTConstants.TOKEN_SECRET,
                                         algorithms=[JWTConstants.JWT_ALGORITHM])
                    request.user_id = payload["user_id"]
                    
                    # if user is deleted
                    if not User.objects.filter(user_id=request.user_id,is_deleted=0):
                        response = Response({'message': Messages.USER_DOES_NOT_EXISTS},
                                    content_type="application/json", status=status.HTTP_401_UNAUTHORIZED)
                        return ErrorResponse(response)

                    # Token is valid pass the request
                    return function(request, *args, **kwargs)
                
                except jwt.exceptions.DecodeError: 
                    response = Response({'message':Messages.INVALID_ACCESS_TOKEN},
                                    content_type="application/json", status=status.HTTP_401_UNAUTHORIZED)
                    return ErrorResponse(response)
                except jwt.exceptions.InvalidSignatureError:  
                    response = Response({'message': Messages.INVALID_ACCESS_TOKEN},
                                    content_type="application/json", status=status.HTTP_401_UNAUTHORIZED)
                    return ErrorResponse(response)
                except jwt.exceptions.ExpiredSignatureError:  
                    response = Response({'message': Messages.ACCESS_TOKEN_EXPIRED},
                                    content_type="application/json", status=status.HTTP_403_FORBIDDEN)
                    return ErrorResponse(response)
                except jwt.exceptions.InvalidTokenError:  
                    response = Response({'message': Messages.INVALID_ACCESS_TOKEN},
                                    content_type="application/json", status=status.HTTP_401_UNAUTHORIZED)
                    return ErrorResponse(response)
            else:
                response = Response({'message': Messages.AUTH_CRED_NOT_PROVIDED},
                                content_type="application/json", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return ErrorResponse(response)
        except BaseException as e:
            response = Response({'message': str(e)}, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)
            return ErrorResponse(response)

    return wrap


def ErrorResponse(response):
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {}
    return response

