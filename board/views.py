from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .permission import *

from .serializers import *

class BoardView(viewsets.ModelViewSet):
    
    queryset=Board.objects.all()

    def get_permissions(self):

        """
        Providing Permissions According To UserType
        """

        if self.action in ['destroy', 'update', 'partial_update']:
            permissions_classes = [IsOwnerOrAdmin]


        elif self.action =='retrieve':
            permissions_classes = [IsMemberOrAdmin]

        elif self.action=='create':
            permissions_classes=[IsAuthenticated]
        
        elif self.action=='list':
            permissions_classes=[IsAdmin]

        else:
            return super().get_permissions()

        return [permissions() for permissions in permissions_classes]
    
    def get_serializer_class(self):
        if self.action in ['create','update']:
            return BoardSerializer
        else:
            return BoardDetailSerializer

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
            )

    @action(methods=['get'], detail=True,permission_classes=[IsOwnerOrAdmin])
    def members(self, request,pk):

        board=get_object_or_404(Board,id=pk)
        excluded_filter = Q(id__in=[user.id for user in board.members.all() ])

        user_instance=User.objects.exclude(excluded_filter)

        if user_instance:
            user_instance_serialized=UserDetailSerializer(user_instance,many=True)
            return Response(user_instance_serialized.data)
        
        return Response({"detail":"No member to do."})
    
class TagView(viewsets.ModelViewSet):
    
    queryset=Tag.objects.all()
    serializer_class=TagSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['board__id']
    search_fields = ['board__id']

    def get_permissions(self):

        """
        Providing Permissions According To UserType
        """

        if self.action in ['destroy', 'update', 'partial_update','retrieve','create']:
            permissions_classes = [IsMemberOrAdmin]
        
        elif self.action in ['list']:
            permissions_classes=[IsAdmin]

        else:
            return super().get_permissions()

        return [permissions() for permissions in permissions_classes]

class ColumnView(viewsets.ModelViewSet):
    
    queryset=Column.objects.all()
    serializer_class=ColumnSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['board']
    search_fields = ['board']

    def get_permissions(self):

        """
        Providing Permissions According To UserType
        """

        if self.action in ['destroy', 'update', 'partial_update','retrieve','create']:
            permissions_classes = [IsOwnerOrAdmin]
        
        elif self.action in ['list']:
            permissions_classes=[IsAdmin]

        else:
            return super().get_permissions()

        return [permissions() for permissions in permissions_classes]
    

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

    def get_permissions(self):

        """
        Providing Permissions According To UserType
        """

        if self.action in ['destroy', 'update', 'partial_update','retrieve','create']:
            permissions_classes = [IsMemberOrAdmin]
        
        elif self.action=='list':
            permissions_classes=[IsAdmin]

        else:
            return super().get_permissions()

        return [permissions() for permissions in permissions_classes]

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

    def get_permissions(self):

        """
        Providing Permissions According To UserType
        """

        if self.action in ['destroy', 'update', 'partial_update']:
            permissions_classes = [IsOwnerOrAdmin]


        elif self.action in['retrieve','create','list']:
            permissions_classes = [IsMemberOrAdmin]

       

        else:
            return super().get_permissions()

        return [permissions() for permissions in permissions_classes]


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)




class BoardDetailView(APIView):
    permission_classes=[IsMemberOrAdmin]
   
    def get(self, request, *args, **kwargs):
        # get board id and user_id for filter
        board_id=kwargs.get('pk','')
        user_id = request.query_params.get('user_id', '')

        # get board object and serialize
        if board_id:
            board_instance=get_object_or_404(Board,id=board_id)
            board_serialized=BoardDetailSerializer(board_instance)
            board_serialized_data=board_serialized.data.copy()

            # fetch column of respective board
            column_instance=Column.objects.filter(board=board_instance.id)
            if column_instance:
                board_serialized_data[Column._meta.db_table]=[]
                column_overall_data=[]
                # fetch card with respect to column
                for col_instance in column_instance:
                    column_serialized=ColumnSerializer(col_instance)
                    column_serialized_data=column_serialized.data.copy()
                    column_card=Card.objects.filter(column=col_instance.id)
                    
                    # filter card if user_id is filter params
                    if user_id:
                        column_card=column_card.filter(assignees__id=user_id)
                    
                    column_card_serialized=CardDetailSerializer(column_card,many=True)
                    column_serialized_data[Card._meta.db_table]=column_card_serialized.data

                    column_overall_data.append(column_serialized_data)
                

                board_serialized_data[Column._meta.db_table]= column_overall_data


            return Response(board_serialized_data)
        
        return Response({"error":"Board id is required"})

