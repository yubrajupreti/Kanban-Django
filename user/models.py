from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Permission
from django.core.validators import MinLengthValidator


from base.models import Extensions


def profile_image_path(instance, filename):
    return "users/profile_image/{}/{}".format(instance.uuid, filename)

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError("The email must be set")
        if not password:
            raise ValueError("The password must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **extra_fields)
        user.set_password(password)
        user.save()

        if user.is_superuser:
            user.user_permissions.set(Permission.objects.all())
            user.save()


        return user

    def create_normal(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_normal=True
        )
        return user


    def create_staffuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_admin', True)




        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin,Extensions):

    """
    Models for users
    """

    GENDER_TYPE = (
        ('male', 'male'),
        ('female', 'female'),
        ('other', 'other')
    )

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(validators=[MinLengthValidator(7)], max_length=10, null=True, unique=True)
    gender=models.CharField(max_length=25,choices=GENDER_TYPE)
    profile_picture=models.ImageField(upload_to=profile_image_path,blank=True,null=True)

    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_admin=models.BooleanField(default=False)



    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = verbose_name

    
    def get_full_name(self):
        return "{} {} {}".format(self.first_name,self.middle_name,self.last_name)

    def get_short_name(self):
        return self.first_name


    def __str__(self):
        return self.email
