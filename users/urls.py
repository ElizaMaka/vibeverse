from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, LoginView, UserUpdateViewset, FollowUserView, UserDetailViewset, ProfileSetUpViewSet

router = DefaultRouter()
router.register(r'register', RegisterView, basename='register')
router.register(r'user-update', UserUpdateViewset, basename='user-update')
router.register(r'me', UserDetailViewset, basename='me')
router.register(r'user/profile-setup', ProfileSetUpViewSet, basename='user.profile-setup')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('follow/', FollowUserView.as_view()),
]