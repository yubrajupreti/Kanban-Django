from rest_framework import viewsets
from .serializers import *

class BoardView(viewsets.ModelViewSet):
    
    queryset=Board.objects.all()
    serializer_class=BoardSerializer

class TagView(viewsets.ModelViewSet):
    
    queryset=Tag.objects.all()
    serializer_class=TagSerializer

class ColumnView(viewsets.ModelViewSet):
    
    queryset=Column.objects.all()
    serializer_class=ColumnSerializer

class CardView(viewsets.ModelViewSet):
    
    queryset=Card.objects.all()
    serializer_class=CardSerializer


class CommentView(viewsets.ModelViewSet):
    
    queryset=Comment.objects.all()
    serializer_class=CommentSerializer


