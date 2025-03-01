from rest_framework import serializers
from django.db import transaction

from .models import User, Profile

from blog.models import Blog

class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ['user']
    
    def get_followers_count(self, obj):
        user = obj.user
        return Profile.objects.filter(followings=user).values_list('user__id', flat=True).count()

class UserRegisterSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'username', 'profile', 'created_at', 'updated_at']
        read_only_fields = ['username']
        extra_kwargs = {
            'password': {'write_only':True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(
            email=validated_data['email'].lower(),
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.username = f"{validated_data['first_name']}_{validated_data['last_name']}".lower()
        user.set_password(password)
        user.save()
        return user

class ProfileSetUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ['user', 'followers']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    blog_count = serializers.SerializerMethodField()
    followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile', 'blog_count', 'followed']
        read_only = ['username']
        extra_kwargs = {
            'password': {'write_only':True}
        }

    def get_blog_count(self, obj):
        return obj.blogs.count()
    
    def get_followed(self, obj):
        request = self.context.get('request')
        if obj in request.user.profile.followings.all():
            return True
        return False
