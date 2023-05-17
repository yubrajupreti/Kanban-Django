import jwt

from django.contrib.auth import login, logout

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from kanban import settings
from .serializers import *

class UserLoginView(APIView):
    """
    View for Login sytem without implemeting OTP System
    """
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        login(request, user)
    
        refresh = RefreshToken.for_user(user)

        response=Response({
            'access_token': str(refresh.access_token),
            'refresh_token':str(refresh),
            'email': user.email,
            'is_active':user.is_active,
            'is_staff':user.is_staff,
            'is_admin':user.is_active,

        }, status=status.HTTP_200_OK)
        response.set_cookie('access_token',str(refresh.access_token) , httponly=True, samesite='Lax')
        response.set_cookie('refresh_token',str(refresh) , httponly=True, samesite='Lax')

        return response

       


class UserLogoutView(APIView):
    """
    View for Logout System for user
    """
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        logout(request)
        return Response({'detail': "Successfully logout"}, status=204)



class VerifyEmail(APIView):
    """
	View For EmailVerification for user
	"""
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token')
        try:
            algorithms = ['HS256']
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms=algorithms)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
               
            return Response(
                {'success': 'Email Successfully activated', 'status': status.HTTP_200_OK},
                status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {'detail': 'Activation Expired', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {'detail': 'Invalid token', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)
