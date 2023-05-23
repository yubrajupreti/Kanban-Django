from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response



from .serializers import *

class BoardView(viewsets.ModelViewSet):
    
    queryset=Board.objects.all()
    serializer_class=BoardSerializer
    
    def get_serializer_class(self):
        if self.action in ['create','update']:
            return BoardSerializer
        else:
            return BoardDetailSerializer

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

    def get_serializer_class(self):
        if self.action in ['list','retrieve']:
            return CardDetailSerializer
        else:
            return CardSerializer


    def perform_create(self, serializer):
        last_instance=Column.objects.filter(column=serializer.initial_data['column']).last()
        if last_instance:
            serializer.save(order=last_instance.order+1)
        else:
            serializer.save(order=1)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        comment_instance=Comment.objects.filter(card=instance)
        card_serializer_data=serializer.data.copy()

        if comment_instance:
            comment_serializer=CommentSerializer(comment_instance,many=True)
            card_serializer_data[Comment._meta.db_table]=comment_serializer.data

        return Response(card_serializer_data)

class CommentView(viewsets.ModelViewSet):
    
    queryset=Comment.objects.all()
    serializer_class=CommentSerializer


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BoardDetailView(APIView):

    def get(self, request, *args, **kwargs):
        board_id=kwargs.get('pk','')
        user_id = request.query_params.get('user_id', '')

        if board_id:
            board_instance=get_object_or_404(Board,id=board_id)
            board_serialized=BoardDetailSerializer(board_instance)
            board_serialized_data=board_serialized.data.copy()

            column_instance=Column.objects.filter(board=board_instance.id)
            if column_instance:
                board_serialized_data[Column._meta.db_table]=[]
                column_overall_data=[]
                for col_instance in column_instance:
                    column_serialized=ColumnSerializer(col_instance)
                    column_serialized_data=column_serialized.data.copy()
                    column_card=Card.objects.filter(column=col_instance.id)

                    if user_id:
                        column_card=column_card.filter(assignees__id=user_id)
                    
                    column_card_serialized=CardDetailSerializer(column_card,many=True)
                    column_serialized_data[Card._meta.db_table]=column_card_serialized.data

                    column_overall_data.append(column_serialized_data)
                

                board_serialized_data[Column._meta.db_table]= column_overall_data


            return Response(board_serialized_data)
        
        return Response({"error":"Board id is required"})

