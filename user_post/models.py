from django.db import models
from auth_user.models import User
from jsonfield import JSONField

# Create your models here.

# This class is used to create the Post model
class Post(models.Model):

    user_posts_id = models.AutoField(primary_key=True)
    content = models.TextField(blank=True, null=True)
    media = JSONField()
    total_like = models.IntegerField(default=False, null=True)
    total_comment = models.IntegerField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, db_column = 'user_id',related_name='user_post_user', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, db_column = 'updated_by',related_name='user_post_updated', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=0,null=False)
    
    class Meta:
        db_table = 'user_posts'


# This class is used to create the Post Reaction model
class PostReaction(models.Model):
 
    post_reactions_id = models.AutoField(primary_key=True)
    user_posts_id = models.ForeignKey(Post, db_column = 'user_posts_id',related_name='post_reaction_user_post', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, db_column = 'user_id',related_name='post_reaction_user', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'post_reactions'


# This class is used to create the Posts Comments model
class PostComment(models.Model):
 
    post_comments_id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=45, blank=True, null=True)
    user_posts_id = models.ForeignKey(Post, db_column = 'user_posts_id',related_name='post_comments_user_post', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, db_column = 'user_id',related_name='post_comment_user', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=0,null=False)
    
    class Meta:
        db_table = 'post_comments'





