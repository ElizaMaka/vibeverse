from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, permission_classes

from .serializers import UserRegisterSerializer, UserUpdateSerializer, UserDetailSerializer, ProfileSetUpSerializer
from .models import User, Profile

# Create your views here.
class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    http_method_names = ['post']

    def post(self, request):
        data = request.data
        serializer = UserRegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
        })
        response.set_cookie(key='access_token', value=access_token, httponly=True, samesite='None', secure=True)
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, samesite='None', secure=True)

        return response

class UserViewset(viewsets.ModelViewSet):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch','get']
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'username', 'profile__bio', 'blogs__title']

class UserDetailViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

class ProfileSetUpViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSetUpSerializer
    http_method_names = ['patch']

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def follow_user(request):
    user = request.user
    user_to_follow_id = request.data.get('user_to_follow_id')

    if not user_to_follow_id:
        return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_to_follow = User.objects.get(id=user_to_follow_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if user == user_to_follow:
        return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
    
    followings = user.profile.followings.all()
    if user_to_follow in followings:
        return Response({"error": f"You are already following {user_to_follow.username}"}, status=status.HTTP_400_BAD_REQUEST)
    
    user.profile.followings.add(user_to_follow)
    return Response({"message": f"You are now following {user_to_follow.username}."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def unfollow_user(request):
    user = request.user
    user_to_unfollow_id = request.data.get('user_to_unfollow_id')

    if not user_to_unfollow_id:
        return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_to_unfollow = User.objects.get(id=user_to_unfollow_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if user == user_to_unfollow:
        return Response({"error": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)
    
    followings = user.profile.followings.all()
    if not user_to_unfollow in followings:
        return Response({"error": f"You have not followed {user_to_unfollow.username}"}, status=status.HTTP_400_BAD_REQUEST)
    
    user.profile.followings.remove(user_to_unfollow)
    return Response({"message": f"You have unfollowed {user_to_unfollow.username}."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def followers(request):
    user = request.user

    followers = Profile.objects.filter(followings=user)
    if followers:
        data = []
        for follower in followers:
            user = User.objects.get(id = follower.user.id)
            serializer = UserDetailSerializer(user)
            data.append(serializer.data)
        return Response(data)
    
    return Response([], status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def followings(request):
    user = request.user
    followings = user.profile.followings.all()
    if followings:
        serializer = UserDetailSerializer(followings, many=True)
        return Response(serializer.data)
    
    return Response([], status=status.HTTP_200_OK)




