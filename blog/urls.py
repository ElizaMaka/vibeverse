from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BlogViewSet, RecentBlogsViewSet, AllBlogsViewSet, FeedBlogsViewSet, like_blogs, unlike_blogs

router = DefaultRouter()
router.register(r'blog', BlogViewSet, basename='blog')
router.register(r'recent', RecentBlogsViewSet, basename='recent')
router.register(r'all', AllBlogsViewSet, basename='all')
router.register('feed-blogs', FeedBlogsViewSet, basename='feed_blogs')

urlpatterns = [
    path('like/<blog_id>/', like_blogs),
    path('unlike/<blog_id>/', unlike_blogs),
    path('', include(router.urls)),
]
