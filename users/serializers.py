from rest_framework import serializers
from django.db import transaction

from .models import User, Profile

from blog.models import Blog

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'username']
        extra_kwargs = {
            'password': {'write_only':True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(
            email=validated_data['email'],
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

class ProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = "__all__"
    
    def get_followers_count(self, obj):
        user = obj.user
        return Profile.objects.filter(followings=user).values_list('user__id', flat=True).count()


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    blog_count = serializers.SerializerMethodField()
    followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'profile', 'blog_count', 'followed']
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

    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)

        if profile_data:
            profile_instance = instance.profile
            followers = profile_data.pop('followers', None)
            if followers is not None:
                profile_instance.followers.set(followers)
            for attr, value in profile_data.items():
                setattr(profile_instance, attr, value)
            profile_instance.save()
        
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    blog_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'profile', 'blog_count']
        extra_kwargs = {
            'password': {'write_only':True}
        }
    
    def get_blog_count(self, obj):
        return obj.blogs.count()
