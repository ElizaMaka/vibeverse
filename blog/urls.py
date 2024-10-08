from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BlogImageViewSet, BlogViewSet, FeedBlogsViewSet, like_blogs, unlike_blogs, AddBlogReviewViewSet, YouMayLikeBlogViewSet, popular_tags

router = DefaultRouter()
router.register(r'blog', BlogViewSet, basename='blog')
router.register('images', BlogImageViewSet, basename='images')
router.register('feed-blogs', FeedBlogsViewSet, basename='feed-blogs')
router.register('add-review', AddBlogReviewViewSet, basename='add-review')
router.register('you-may-like', YouMayLikeBlogViewSet, basename='you-may-like')

urlpatterns = [
    path('like/<blog_id>/', like_blogs),
    path('unlike/<blog_id>/', unlike_blogs),
    path('', include(router.urls)),
    path('popular-tags/', popular_tags)
]
