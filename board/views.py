from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView

from .serializers import *

class BoardView(viewsets.ModelViewSet):
    
    queryset=Board.objects.all()
    serializer_class=BoardSerializer


    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
            )

class TagView(viewsets.ModelViewSet):
    
    queryset=Tag.objects.all()
    serializer_class=TagSerializer

class ColumnView(viewsets.ModelViewSet):
    
    queryset=Column.objects.all()
    serializer_class=ColumnSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['board']
    search_fields = ['board']

    def perform_create(self, serializer):
        last_instance=Column.objects.filter(board=serializer.initial_data['board']).last()
        if last_instance:
            serializer.save(order=last_instance.order+1)
        else:
            serializer.save(order=1)

class CardView(viewsets.ModelViewSet):
    
    queryset=Card.objects.all()
    serializer_class=CardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['column','assignees__uuid']
    search_fields = ['column']

    def perform_create(self, serializer):
        last_instance=Column.objects.filter(column=serializer.initial_data['column']).last()
        if last_instance:
            serializer.save(order=last_instance.order+1)
        else:
            serializer.save(order=1)

class CommentView(viewsets.ModelViewSet):
    
    queryset=Comment.objects.all()
    serializer_class=CommentSerializer



