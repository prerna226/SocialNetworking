from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    path('posts', views.UserPosts.as_view()),
    path('posts/reaction', views.PostReactions.as_view()),
    path('posts/comments', views.PostComments.as_view())

]

urlpatterns += router.urls
