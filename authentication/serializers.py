from django.contrib.auth import authenticate

from rest_framework import serializers
from user.models import User



class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if user.is_active and user.is_verified:
                    data["user"] = user
                else:
                    msg="Please verify your email"
                    raise serializers.ValidationError(msg)

            else:
                msg="The email and password is not registered"
                raise serializers.ValidationError(msg)
        else:
            msg = "Please provide email and password"
            raise serializers.ValidationError(msg)

        return data



class EmailVerificationSerializer(serializers.Serializer):
	token = serializers.CharField(max_length=255)

	class Meta:
		model = User
		fields = ['token']
