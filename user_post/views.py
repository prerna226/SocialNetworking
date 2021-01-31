
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from utility.authMiddleware import isAuthenticate
from utility.requestErrorFormate import requestErrorMessagesFormate
from utility.jwtTokenHelper import JwtTokenHelper
from utility.sqlQueryBuilder import SqlQueryBuilder
from user_auth.models import(User)
from .models import (Post,PostComment,PostReaction)
from config.messages import Messages
from django.views.decorators.csrf import csrf_exempt
from cerberus import Validator
from django.db import transaction
from django.db.models import Q


# Create your views here.

# This class is used to create, update and get user post
class UserPosts(APIView):
    
    # to create post
    @method_decorator(isAuthenticate)
    def post(self, request):  
        try:
            schema = {
            "content": {'type': 'string', 'required': True, 'empty': True},
            "media": {'type': 'list', 'required': True, 'empty': True}
            }
            v = Validator()
            if request.data['content'] == "" and len(request.data['media']) == 0:
                return Response({'error':Messages.PLEASE_ADD_SOME_THING}, status=status.HTTP_200_OK)
            if not v.validate(request.data, schema):
                return Response(requestErrorMessagesFormate(v.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = request.META['HTTP_AUTHORIZATION']  # get token from header
            payload = JwtTokenHelper().getJWTPayload(token)  # get userId from payload
            user_id = payload["user_id"]
            Post.objects.create(
                content=request.data['content'],
                media=request.data['media'],
                user_id=User.objects.get(user_id=user_id)
            )
            return Response({'message': Messages.POST_CREATED}, status=status.HTTP_200_OK)
        except Exception as e:
            print('...................post created exception........',str(e))
            return Response({'error': Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    # to update post
    @method_decorator(isAuthenticate)
    def put(self, request):  
        try:
            schema = {
                "user_post_id": {'type': 'integer', 'required': True, 'empty': True},
                "content": {'type': 'string', 'required': True, 'empty': True}
            }
            v = Validator()
            if request.data['content'] == "" and len(request.data['media']) == 0:
                return Response({'error':Messages.PLEASE_ADD_SOME_THING}, status=status.HTTP_200_OK)
            if not v.validate(request.data, schema):
                return Response(requestErrorMessagesFormate(v.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = request.META['HTTP_AUTHORIZATION']  # get token from header
            payload = JwtTokenHelper().getJWTPayload(token)  # get userId from payload
            user_id = payload["user_id"]
            if Post.objects.filter(user_posts_id=request.data['user_post_id'],is_deleted=0 ).exists():
                if Post.objects.filter(user_posts_id=request.data['user_post_id'],user_id=user_id ).exists():
                    Post.objects.filter(user_posts_id = request.data['user_post_id']).update(
                        content=request.data['content']
                    )
                    return Response({'message': Messages.POST_UPDATED}, status=status.HTTP_200_OK)
                return Response({'error': Messages.CAN_NOT_EDIT_POST}, status=status.HTTP_200_OK)
            return Response({'error': Messages.POST_DOES_NOT_EXIST}, status=status.HTTP_200_OK)
        except Exception as e:
            print('...................post updated exception........',str(e))
            return Response({'error': Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    # get the user post listing
    @method_decorator(isAuthenticate)
    def get(self, request): 
        try:
            result = []
            finalResult = []
            totalReaction = []
            request.page_offset = int(request.GET["page_offset"]) if request.GET["page_offset"] else 1
            request.page_limit = int(request.GET["page_limit"]) if request.GET["page_limit"] else 100

            schema = {
                "search_text": {'type': 'string', 'required': True, 'empty':True},
                "page_limit": {'type': 'integer', 'required': True, 'empty': True},
                "page_offset": {'type': 'integer', 'required': True, 'empty': True}
            }
            instance = {
                "search_text":request.GET['search_text'],
                "page_limit": request.page_limit,
                "page_offset": request.page_offset
            }
            v = Validator()
            if not v.validate(instance, schema):
                return Response(requestErrorMessagesFormate(v.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            db = SqlQueryBuilder()
            token = request.META['HTTP_AUTHORIZATION']  # get token from header
            payload = JwtTokenHelper().getJWTPayload(token)  # get userId from payload
            login_user_id = payload["user_id"]
            search_text = request.GET['search_text']
            page_limit = request.page_limit
            page_offset = request.page_offset
            post_result = db.readProcedureJson('spPostListing',[search_text,page_limit,page_offset,login_user_id ])
            db.commit()
            if len(post_result)>0:
                finalResult = {'data':post_result}
                return Response(finalResult, status=status.HTTP_200_OK)
            else:
                return Response({'message':Messages.NO_RECORD}, status=status.HTTP_200_OK)
        except Exception as e:
            print('...................post listing excep........',str(e))
            return Response({'error': Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# This class is used to react on the post
class PostReactions(APIView):
    
    # to like/unlike on post
    @method_decorator(isAuthenticate)
    def post(self, request):  
        try:
            schema = {
            "user_post_id": {'type': 'integer', 'required': True, 'nullable':False},
            "like_status": {'type': 'integer', 'required': True, 'nullable':False,'allowed':[0,1]}
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response(requestErrorMessagesFormate(v.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            db = SqlQueryBuilder()
            token = request.META['HTTP_AUTHORIZATION']  # get token from header
            payload = JwtTokenHelper().getJWTPayload(token)  # get userId from payload
            user_id = payload["user_id"]
            
            if Post.objects.filter(user_posts_id=request.data['user_post_id'],is_deleted=0 ).exists():

                post_detail = Post.objects.filter(user_posts_id=request.data['user_post_id']).values()
                total_likes = post_detail[0]['total_like']
            
                # to like the post
                if int(request.data['like_status']) == 1:
                    if not PostReaction.objects.filter(user_posts_id=request.data['user_post_id'],user_id=user_id).exists():
                    
                        with transaction.atomic():
                            
                            # insert in post reaction table
                            PostReaction.objects.create(
                                user_posts_id = Post.objects.get(user_posts_id=request.data['user_post_id']),
                                user_id = User.objects.get(user_id=user_id)
                            )
                            
                            # increase likes count
                            if total_likes >= 0:
                                Post.objects.filter(user_posts_id=request.data['user_post_id']).update(total_like=total_likes+1)
                            return Response({'message': Messages.POST_LIKED}, status=status.HTTP_200_OK)
                    return Response({'error': Messages.POST_ALREADY_LIKED}, status=status.HTTP_200_OK)
            
                # to remove like 
                elif int(request.data['like_status']) == 0:

                    with transaction.atomic():
                        
                        PostReaction.objects.filter(user_posts_id=request.data['user_post_id']).delete()
                        post_detail = Post.objects.filter(user_posts_id=request.data['user_post_id']).values()
                        
                        # decrease likes count
                        if total_likes > 0:
                            Post.objects.filter(user_posts_id=request.data['user_post_id']).update(total_like=total_likes-1)                
                        return Response({'message': Messages.LIKE_REMOVED}, status=status.HTTP_200_OK)
            
            return Response({'error': Messages.POST_DOES_NOT_EXIST}, status=status.HTTP_200_OK)

        except Exception as e:
            print('...................react on post exception........',str(e))
            return Response({'error': Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# This class is used to comment on the post
class PostComments(APIView):
    
    # to comment on the post
    @method_decorator(isAuthenticate)
    def post(self, request):  
        try:
            schema = {
            "user_post_id": {'type': 'integer', 'required': True, 'nullable':False},
            "comment": {'type': 'string', 'required': True, 'empty':False}
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response(requestErrorMessagesFormate(v.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            db = SqlQueryBuilder()
            token = request.META['HTTP_AUTHORIZATION']  # get token from header
            payload = JwtTokenHelper().getJWTPayload(token)  # get userId from payload
            user_id = payload['user_id']

            if Post.objects.filter(user_posts_id=request.data['user_post_id'],is_deleted=0 ).exists():
            
                # insert into post comment table
                PostComment.objects.create(
                    comment=request.data['comment'],
                    user_posts_id = Post.objects.get(user_posts_id=request.data['user_post_id']),
                    user_id=User.objects.get(user_id=user_id)
                )

                post_detail = Post.objects.filter(user_posts_id=request.data['user_post_id']).values()
                total_comments = post_detail[0]['total_comment']

                # increase post comment count
                if total_comments >= 0:
                    Post.objects.filter(user_posts_id=request.data['user_post_id']).update(total_comment=total_comments+1)
                
                return Response({'message': Messages.POST_COMMENTED}, status=status.HTTP_200_OK)
            return Response({'error': Messages.POST_DOES_NOT_EXIST}, status=status.HTTP_200_OK)

        except Exception as e:
            print('...................comment on the post exception........',str(e))
            return Response({'error': Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # get the post comments with reply 
    @method_decorator(isAuthenticate)
    def get(self, request): 
        try:
            result = []
            finalResult = []
            totalReply = []
            request.page_offset = int(request.GET["page_offset"]) if request.GET["page_offset"] else 1
            request.page_limit = int(request.GET["page_limit"]) if request.GET["page_limit"] else 100

            schema = {
                "user_post_id": {'type': 'integer', 'required': True, 'nullable': False},
                "page_limit": {'type': 'integer', 'required': True, 'empty': True},
                "page_offset": {'type': 'integer', 'required': True, 'empty': True}
            }
            instance = {
                "user_post_id":int(request.GET['user_post_id']),
                "page_limit": request.page_limit,
                "page_offset": request.page_offset
            }
            v = Validator()
            if not v.validate(instance, schema):
                return Response(requestErrorMessagesFormate(v.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            db = SqlQueryBuilder()
            page_limit = request.page_limit
            page_offset = request.page_offset
            commentResult = db.readProcedureJson('spCommentListing',[page_limit,page_offset,request.GET['user_post_id']])
            db.commit()
            if len(commentResult)>0:
                finalResult = {
                    'data':commentResult,
                }
                return Response(finalResult, status=status.HTTP_200_OK)
            else:
                return Response({'message':Messages.NO_RECORD}, status=status.HTTP_200_OK)
        except Exception as e:
            print('...................post comments with reply exception........',str(e))
            return Response({'error': Messages.SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


