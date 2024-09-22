from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q

from .models import Blog, BlogImage, BlogReview
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

class ViewBlogReviewsViewSet(viewsets.ModelViewSet):
    queryset = BlogReview.objects.all()
    serializer_class = BlogReviewSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        blog_id = request.query_params.get('blog_id')

        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            raise ValidationError({"message":"Invalid Blog id"})
        

        reviews = BlogReview.objects.filter(blog=blog)
        serializer = BlogReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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