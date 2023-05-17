from django.urls import path, include

from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views


from .views import UserRegisterView


router=routers.DefaultRouter()
router.register('users', UserRegisterView, basename='users')



urlpatterns = [
	path('token/create/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
	path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
	path('', include(router.urls)),

	path('api-auth/', include('rest_framework.urls',namespace='rest_framework)')),

]