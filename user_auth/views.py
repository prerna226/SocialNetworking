import uuid, jwt
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from utility.authMiddleware import isAuthenticate
from utility.jwtTokenHelper import JwtTokenHelper
from utility.passwordHashing import PasswordHashing
from config.messages import Messages
from .models import (User,Device)
from utility.requestErrorFormate import requestErrorMessagesFormate
from django.views.decorators.csrf import csrf_exempt
from cerberus import Validator
from django.db.models import Q
from django.db import transaction

# This method is used for sign-up
@api_view(['POST'])
def sign_up(request):

    try:
        schema = {
            "first_name": {'type': 'string', 'required': True, 'empty': False},
            "last_name": {'type': 'string', 'required': True, 'empty': False},
            "email": {'type': 'string', 'required': True, 'empty':False},
            "password": {'type': 'string', 'required': True, 'empty': True},
            "device_token": {'type': 'string', 'required': True, 'empty': False},
            "device_type": {'type': 'integer', 'required': True, 'nullable': False}
        }

        v = Validator()
        if not v.validate(request.data, schema):
            return Response(requestErrorMessagesFormate(v.errors), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    try:

        # check if email exists
        if User.objects.filter(email=request.data['email'].lower()).exists():
            return Response({'error':Messages.EMAIL_EXISTS}, status=status.HTTP_200_OK)
        

        # Convert password into hash sha256
        hash_password = PasswordHashing().getHashedPassword(request.data['password'])  # Convert password into hash sha256

        with transaction.atomic():

            # insert data in user table
            User.objects.create(
                email=request.data['email'].lower(),
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                password = hash_password
            )
            user_info = User.objects.filter(email=request.data['email']).values()
            
            token_data = access_refresh_token(user_info[0]['user_id'])
            
            # insert data in device table
            Device.objects.create(
                refresh_token=token_data['refresh_token'],
                device_type = request.data['device_type'],
                device_token=request.data['device_token'],
                user_id=User.objects.get(user_id=user_info[0]['user_id'])
            )

            return Response({'user_id':user_info[0]['user_id'],'access_token':token_data['access_token'],'refresh_token':token_data['refresh_token']}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print('............................sign up excep.......',str(e))
        return Response({'error':Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# This method is used for login
@csrf_exempt
@api_view(['POST'])
def sign_in(request):
    try:
        schema = {
            "email": {'type': 'string', 'required': True, 'empty': False},
            "password": {'type': 'string', 'required': True, 'empty': False},
            "deviceToken": {'type': 'string', 'required': True, 'empty': False},
            "deviceType": {'type': 'integer', 'required': True, 'nullable': False},
            
        }
        v = Validator()
        if not v.validate(request.data, schema):
            return Response(requestErrorMessagesFormate(v.errors), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    try:
        passwordHashing = PasswordHashing()
        
        # if user already registered
        user_information = User.objects.filter(email=request.data['email']).values()
       
        if user_information:
            user_id = user_information[0]['user_id']
            user_password = user_information[0]['password']
            email = user_information[0]['email']
            firstName = user_information[0]['first_name']
            lastName = user_information[0]['last_name']
        else:
            return Response({'error':Messages.PASSWORD_OR_EMAIL_INCORRECT}, status=status.HTTP_200_OK)


            
        # match the password, if same then continue
        if passwordHashing.matchHashedPassword(user_password,request.data['password']):

            token_data = access_refresh_token(user_id)

            with transaction.atomic():
                
                # insert data in device table
                Device.objects.create(
                refresh_token=token_data['refresh_token'],
                device_type = request.data['device_type'],
                device_token=request.data['device_token'],
                user_id=User.objects.get(user_id=user_information[0]['user_id'])
            )

                data = {
                    "user_id":user_information[0]['user_id'],
                    "access_token": token_data['access_token'],
                    "refresh_token": token_data['refresh_token']
                }

                return Response(data, status=status.HTTP_200_OK)
        return Response({'error':Messages.PASSWORD_OR_EMAIL_INCORRECT}, status=status.HTTP_200_OK)
        
    except Exception as e:
        print('............................login exception.......',str(e))
        return Response({'error':Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def access_refresh_token(user_id):
   
    try:
        # generate access token
        access_token = JwtTokenHelper().JWTAccessToken(user_id) 
        # generate refresh token
        refresh_token = JwtTokenHelper().JWTRefreshToken(user_id)  

        data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            
        }
        return data
    except Exception as e:
        print('................logs................',str(e))
        return Response({'message': Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



