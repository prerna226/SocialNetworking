from django.db import models

# Create your models here.

# This class is used to create the User model
class User(models.Model):
    
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_deleted = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        db_table = 'users'

#  This class is use for create the preference model
class Device(models.Model):

    device_id = models.AutoField(primary_key=True)
    refresh_token = models.CharField(max_length=500,default=False, null=True)
    device_type = models.BooleanField(default=True) # 1--> for android , 0--> ios
    device_token = models.CharField(max_length=255,blank=True)
    user_id =  models.ForeignKey(User, db_column = 'user_id',related_name='device_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True,null=False)
    
    
    class Meta:
        db_table = 'device'

