from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BlogImageViewSet, BlogViewSet, RecentBlogsViewSet, AllBlogsViewSet, FeedBlogsViewSet, like_blogs, unlike_blogs, AddBlogReviewViewSet, ViewBlogReviewsViewSet, YouMayLikeBlogViewSet

router = DefaultRouter()
router.register(r'blog', BlogViewSet, basename='blog')
router.register('images', BlogImageViewSet, basename='images')
router.register(r'recent', RecentBlogsViewSet, basename='recent')
router.register(r'all', AllBlogsViewSet, basename='all')
router.register('feed-blogs', FeedBlogsViewSet, basename='feed-blogs')
router.register('add-review', AddBlogReviewViewSet, basename='add-review')
router.register('view-review', ViewBlogReviewsViewSet, basename='view-review')
router.register('you-may-like', YouMayLikeBlogViewSet, basename='you-may-like')

urlpatterns = [
    path('like/<blog_id>/', like_blogs),
    path('unlike/<blog_id>/', unlike_blogs),
    path('', include(router.urls)),
]
