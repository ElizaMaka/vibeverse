from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError

from .models import Blog
from .serializers import BlogSerializer

from users.models import User

# Create your views here.
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Blog.objects.filter(user=self.request.user)


class RecentBlogsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id is None:
            raise NotFound(detail="user_id parameter is required.")
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFound(detail=f"User with id {user_id} does not exist.")
        
        return Blog.objects.filter(user=user).order_by('-created_at')[:5]

class AllBlogsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id is None:
            raise NotFound(detail="user_id parameter is required.")
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFound(detail=f"User with id {user_id} does not exist.")
        
        return Blog.objects.filter(user=user)

class FeedBlogsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        followings = user.profile.followings.all()
        followings_blogs = Blog.objects.filter(user__in=followings)
        return followings_blogs