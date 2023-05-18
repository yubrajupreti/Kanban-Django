from django.urls import path, include

from rest_framework import routers


from .views import *


router=routers.DefaultRouter()
router.register('board', BoardView, basename='board')
router.register('tag', TagView, basename='tag')
router.register('column', ColumnView, basename='column')
router.register('card', CardView, basename='card')
router.register('comment', CommentView, basename='comment')


urlpatterns = [

	path('', include(router.urls))
]