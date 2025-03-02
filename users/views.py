from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action

from .serializers import UserRegisterSerializer, UserSerializer, ProfileSetUpSerializer
# from .serializers import UserRegisterSerializer, UserUpdateSerializer, UserDetailSerializer, ProfileSetUpSerializer
from .serializers import UserRegisterSerializer
from .models import User, Profile

# Create your views here.
class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email__iexact=email).first()
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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name', 'username', 'profile__bio', 'blogs__title']

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        user = self.get_serializer(request.user)
        return Response(user.data)
    
    @action(detail=False, methods=['get'], url_path='followers')
    def followers(self, request):
        user = request.user

        followers = Profile.objects.filter(followings=user)
        if followers:
            data = []
            for follower in followers:
                user = User.objects.get(id = follower.user.id)
                serializer = UserSerializer(user, context={'request':request})
                data.append(serializer.data)
            return Response(data)
        return Response([], status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['get'], url_path='followings')
    def followings(self, request):
        user = request.user
        followings = user.profile.followings.all()
        if followings:
            serializer = UserSerializer(followings, many=True, context={'request':request})
            return Response(serializer.data)
        return Response([], status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='follow')
    def follow_user(self, request):
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
    

    @action(detail=False, methods=['post'], url_path='unfollow')
    def unfollow_user(self, request):
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

class ProfileSetUpViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSetUpSerializer
    http_method_names = ['patch']



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def logout(request):
    # Get the refresh token from cookies
    raw_token = request.COOKIES.get('refresh_token', None)

    # Attempt to blacklist the refresh token
    if raw_token:
        try:
            token = RefreshToken(raw_token.encode('utf-8'))
            token.blacklist()
        except Exception as e:
            response = JsonResponse({"message": "Logout successful"}, status=status.HTTP_200_OK)
            response.delete_cookie("access_token", path='/')
            response.delete_cookie("refresh_token", path='/')
            return response

    # Clear session
    request.session.flush()  # Clear session data

    # Delete the cookies
    response = JsonResponse({"message": "Logout successful"}, status=status.HTTP_200_OK)
    response.delete_cookie("access_token", path='/')
    response.delete_cookie("refresh_token", path='/')

    return response