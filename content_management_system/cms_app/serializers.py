from rest_framework import serializers
from .models import *



class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUser
        fields = ['user_id', 'username', 'password', 'name', 'email', 'contact_no', 'city']


class BlogSerializer(serializers.ModelSerializer):

    # like = serializers.PrimaryKeyRelatedField(many = True, read_only = True, source = 'like_set')
    like = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ['post_id', 'title', 'description', 'content', 'is_public', 'creation_date', 'updated_at', 'like', 'like_count', 'owner']
    
    def get_like(self, obj):
        likes = obj.like_set.all()
        return [{'like_id': like.like_id, 'user_name': like.user.name} for like in likes]
    
    def get_like_count(self, obj):
        
        return obj.like_set.count()
    

class LikeSerializer(serializers.ModelSerializer):
    Liked_by = serializers.ReadOnlyField(source='user.name')

    class Meta:
        model = Like
        fields = '__all__'