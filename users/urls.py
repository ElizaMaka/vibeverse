from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, LoginView, UserViewset, ProfileSetUpViewSet, logout
# from .views import RegisterView, LoginView, UserViewset, follow_user, UserDetailViewset, ProfileSetUpViewSet, unfollow_user, followers, followings

router = DefaultRouter()
router.register('register', RegisterView, basename='register')
router.register('', UserViewset, basename='user')
router.register('profile-setup', ProfileSetUpViewSet, basename='user.profile-setup')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('logout/', logout)
]