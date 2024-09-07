from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BlogViewSet, RecentBlogsViewSet, AllBlogsViewSet

router = DefaultRouter()
router.register(r'blog', BlogViewSet, basename='blog')
router.register(r'recent', RecentBlogsViewSet, basename='recent')
router.register(r'all', AllBlogsViewSet, basename='all')

urlpatterns = [
    path('', include(router.urls)),
]
