from django.urls import path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()

urlpatterns = [
    path('sign-up', views.sign_up),
    path('sign-in', views.sign_in)

]

urlpatterns += router.urls
