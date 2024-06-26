from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, filters

from .serializers import UserRegisterSerializer, UserUpdateSerializer, ProfileSerializer, UserDetailSerializer, ProfileSetUpSerializer
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
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

class ProfileSetUpViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSetUpSerializer
    http_method_names = ['patch']
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id' 

    def get_queryset(self):
        user_id = self.kwargs.get(self.lookup_url_kwarg)
        return Profile.objects.filter(user__id=user_id)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get()
        self.check_object_permissions(self.request, obj)
        return obj

class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_to_follow_id = request.data.get('user_to_follow_id')

        if not user_to_follow_id:
            return Response({"error": "user_to_follow_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_to_follow = User.objects.get(pk=user_to_follow_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        profile_to_follow = get_object_or_404(Profile, user=user_to_follow)
        profile_to_follow.followers.add(request.user) 
        profile_to_follow.save() 

        return Response(data={"message":"following"}, status=status.HTTP_204_NO_CONTENT)
