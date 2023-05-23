from django.contrib.auth import get_user_model

from rest_framework import serializers, exceptions


from .models import *

User = get_user_model()




class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context and self.context['view'].action in ['update', 'partial_update']:
            self.fields.pop('email', None)
            self.fields.pop('password', None)

    class Meta:
        fields = ['id','email','first_name','middle_name','last_name','password','contact_number','gender',
                  'is_active','is_verified','is_staff','is_admin','profile_picture'
                  ]
        model = User
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active':{'read_only':True},
            'is_verified': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_admin': {'read_only': True},

        }

   

class UserAdminSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields=UserSerializer.Meta.fields+['user_permissions','groups']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': False},
            'is_verified': {'read_only': False},
            'is_staff': {'read_only': False},
            'is_admin': {'read_only': False},
            
        }


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id','email','first_name','middle_name','last_name','profile_picture']
        model = User

    
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
       

