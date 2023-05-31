from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import EmailMultiAlternatives

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter, OrderingFilter
from board.permission import IsAdmin

from .serializers import UserSerializer, UserAdminSerializer

User = get_user_model()




class UserRegisterView(viewsets.ModelViewSet):
    """
    user view for CRUD operation
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['email']
    search_fields = ['email']
    ordering_fields = ['email']
    lookup_field = 'id'

    def get_serializer_class(self):
        """
        METHOD TO PROVIDE DATA ACCORIDING TO USER TYPE
        """
        user = self.request.user

        try:
            if user.is_admin:
                return UserAdminSerializer

            else:
                return UserSerializer
        except:
            return UserSerializer


    def get_permissions(self):

        """
        Providing Permissions According To UserType
        """

        if self.action in ['create']:
            permissions_classes = [AllowAny]


        elif self.action in ['list','retrieve','update','partial_update','destroy']:
            permissions_classes = [IsAdmin]

        else:
            return super().get_permissions()

        return [permissions() for permissions in permissions_classes]

    def send_mail(self,user,token):
        try:
            subject, from_email, to = 'Verify your Account', 'no-reply@cotiviti.com', user.email
           
            email_body = 'Please verfiy your email - ' + user.email
            current_site = get_current_site(self.request).domain

            absurl = 'http://' + current_site + '/api/verify-email/' + "?token=" + str(token) + "&email=" + user.email
            html_content = f'<p>{email_body}</p>\n<a href="{absurl}">Click here</a>'
            msg = EmailMultiAlternatives(subject, email_body, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return True
        except:
            return False

    

    def perform_create(self, serializer):

        serializer.validated_data['password'] = make_password((serializer.validated_data['password']))
        user = serializer.save(is_active=True)
        user_data = serializer.data
        headers = self.get_success_headers(serializer.data)
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        send_verification_mail=self.send_mail(user,token)
        if send_verification_mail:
            response_data = {
                "success": True,
                "message": "Successfully Registered!! Please check your email for verification.",
                "user": user_data
            }
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

        return Response({"success":False, "message":"Registration Failed. Unable to send verification email."},status=status.HTTP_400_BAD_REQUEST,)


    @action(methods=['get'], detail=False,permission_classes=[IsAuthenticated])
    def profile(self, request, *args, **kwargs):

        """
        METHOD TO GET PROFILE OF USER
        """

        try:
            user = request.user
            if user.is_admin:
                serializer = UserAdminSerializer(user)

            else:
                serializer = UserSerializer(user)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response({'status': 'No detail found for the request user'})


