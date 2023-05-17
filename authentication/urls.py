from django.urls import path, include


from .views import *






urlpatterns = [

	path('verify-email/', VerifyEmail.as_view(), name='verify-email'),
	
	path('login/', UserLoginView.as_view(), name='login'),
	path('logout/', UserLogoutView.as_view(), name='logout'),

]