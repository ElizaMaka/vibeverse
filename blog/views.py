from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from itertools import chain

from .models import Blog, BlogImage, BlogReview, BlogTag
from .serializers import BlogImageSerializer, BlogReviewSerializer, BlogSerializer

from users.models import User

# Create your views here.
class BlogImageViewSet(viewsets.ModelViewSet):
    queryset = BlogImage.objects.all()
    serializer_class = BlogImageSerializer
    permission_classes = [IsAuthenticated]

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['user']
    search_fields = [ 'title', 'tags__tag']

    def get_queryset(self):
        return Blog.objects.all().order_by('-created_at')

class FeedBlogsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        followings = user.profile.followings.all()

        my_recent = Blog.objects.filter(user=user).order_by('-created_at')[:1]
        following_blogs = Blog.objects.filter(user__in=followings)
        blogs = list(chain(my_recent, following_blogs))
        return blogs

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def like_blogs(request, blog_id):
    user = request.user
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        raise ValidationError({'message': 'blog id invalid'})
    
    if user in blog.likes.all():
        return Response({"message": "Already Liked"}, status=status.HTTP_200_OK)
    
    blog.likes.add(user)
    blog.save()
    return Response({"message": "liked"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def unlike_blogs(request, blog_id):
    user = request.user
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        raise ValidationError({'message': 'blog id invalid'})
    
    if not user in blog.likes.all():
        return Response({"message": "you have not liked this blog"}, status=status.HTTP_200_OK)
    
    blog.likes.remove(user)
    blog.save()
    return Response({"message": "unliked"}, status=status.HTTP_200_OK)

class AddBlogReviewViewSet(viewsets.ModelViewSet):
    queryset = BlogReview.objects.all()
    serializer_class = BlogReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog']

class YouMayLikeBlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_interests = self.request.user.profile.interests
        if user_interests:
            user_interests = user_interests.split(',') 
            return (
                Blog.objects.filter(tags__tag__in=user_interests)
                .annotate(matching_tags_count=Count('tags', filter=Q(tags__tag__in=user_interests)))
                .order_by('-matching_tags_count')[:5]
            )
        return None

from rest_framework.response import Response
@api_view(['GET'])
def popular_tags(request):
    tags = BlogTag.objects.annotate(tag_count=Count('blog')).order_by('-tag_count')[:10]
    popular_tags = {tag['tag'] for tag in tags.values('tag')}
    return Response(popular_tags)