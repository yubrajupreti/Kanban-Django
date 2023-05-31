
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from user.serializers import UserDetailSerializer
from .utils import CardSorting
from .models import *

class BoardDetailSerializer(serializers.ModelSerializer):
    members=UserDetailSerializer(many=True,read_only=True)
    owner=UserDetailSerializer(read_only=True)

    class Meta:
        model=Board
        fields='__all__'


    

class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model=Board
        fields='__all__'

    def create_sample_card(self, column_instance):
        
        card_data=[
            {
                "title":"Sample Card",
                "description":"This is a sample card.",
                "assignees":column_instance[0].board.owner,
                "repoter":column_instance[0].board.owner,
                "column":column_instance[0],
                "order":1
            },
             {
                "title":"Sample Card",
                "description":"This is a sample card.",
                "assignees":column_instance[1].board.owner,
                "repoter":column_instance[1].board.owner,
                "column":column_instance[1],
                "order":1
            },
            {
                "title":"Sample Card",
                "description":"This is a sample card.",
                "assignees":column_instance[2].board.owner,
                "repoter":column_instance[2].board.owner,
                "column":column_instance[2],
                "order":1
            }
        ]
        card_instance=[Card(**data)for data in card_data]
        Card.objects.bulk_create(card_instance)


    def create_initial_column(self,instance):

        # create initial column for board
        initial_column=[
            {
                "title":"TO DO",
                "board":instance,
                "order":1
            },
            {
                "title":"IN PROGRESS",
                "board":instance,
                "order":2
            },
            {
                "title":"DONE",
                "board":instance,
                "order":3
            }
        ]

        column_instance=[Column(**data)for data in initial_column]
        instance_list=Column.objects.bulk_create(column_instance)
        return instance_list
    
    def create(self, validated_data):
        # pop for manuplication
        members=validated_data.pop('members',[])

        # creating the board instance before assigning many-to-many field
        instance=Board(**validated_data)
        instance.save()

        # add owner of the board as a user and set it to instance
        members.append(instance.owner)
        instance.members.set(members)

        # create initial column
        column_instance=self.create_initial_column(instance)

        # create sample card
        self.create_sample_card(column_instance)
       
        
        return instance



class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model=Tag
        fields='__all__'

    def validate(self, attrs):
        tag_name=attrs.get('name')

        if Tag.objects.filter(name=tag_name).exists():
            error_message ={"error":f'Tag with {tag_name} already exists.'}
            raise ValidationError(detail=error_message)
        return attrs

class ColumnSerializer(serializers.ModelSerializer,CardSorting):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context and self.context['view'].action in ['create']:
            self.fields.pop('order', None)

    class Meta:
        model=Column
        fields='__all__'

    
    def update(self, instance, validated_data):

        if 'order' in validated_data:
            recent_order=validated_data.get('order')
            previous_order=instance.order
            if previous_order>recent_order:
                
                instance=self.commit_order_changes(
                    previous_order,recent_order,-1,1,instance,validated_data,0
                    )

            elif previous_order<recent_order:
                # 1 indicate the nature of loop
                # 0 indicate the order condition
                # last 0 indicate the column sorting in generic method
                # CardSorting class method is revoked
                instance=self.commit_order_changes(
                    previous_order,recent_order,1,0,instance,validated_data,0
                    )

            return instance

        else:

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()

            return instance
            

        
class CardDetailSerializer(serializers.ModelSerializer):
    assignees=UserDetailSerializer(read_only=True)
    repoter=UserDetailSerializer(read_only=True)
    class Meta:
        model=Card
        fields='__all__'

class CardSerializer(serializers.ModelSerializer,CardSorting):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context and self.context['view'].action in ['create']:
            self.fields.pop('order', None)

    class Meta:
        model=Card
        fields='__all__'
    
    
    def update(self, instance, validated_data):
        if 'column' in validated_data:
            recent_column=validated_data.get('column')
            previous_column=instance.column
            recent_order=validated_data.get('order')
            if recent_column!=previous_column:
                if recent_column.order>previous_column.order:
                    if previous_column.order+1!=recent_column.order:
                        column_apart=get_object_or_404(Column,board=instance.column.board, order=previous_column.order+1)
                        error=f'Column cannot be skipped. It should be moved to {column_apart.title} column.'
                        raise ValidationError(detail=error)
                    
                instance=self.commit_card_column_change(
                    previous_column,recent_column,recent_order,instance,validated_data
                    )
                
                return instance
            
        if 'order' in validated_data:
            recent_order=validated_data.get('order')
            previous_order=instance.order
            if previous_order>recent_order:
                instance=self.commit_order_changes(previous_order,recent_order,-1,1,instance,validated_data,1)


            elif previous_order<recent_order:
                # 1 indicate the nature of loop
                # 0 indicate the order condition
                instance=self.commit_order_changes(previous_order,recent_order,1,0,instance,validated_data,1)

            return instance


        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        return instance
        
    def validate(self, attrs):
        assigned=attrs.get('assignees','')
        reporter=attrs.get('reporter','')
        column=attrs.get('column')
        order=attrs.get('order','')
        board_member=column.board.members.all()

        if order and column:
            card_last_order=Card.objects.filter(column=column).last()
            if order>card_last_order.order:
                error_message = {"error":"Invalid Order"}
                raise ValidationError(detail=error_message)


        if assigned:
            if assigned not in board_member:
                error_message = {"error":"Assigned user is not a member of board"}
                raise ValidationError(detail=error_message)
        if reporter:
            if reporter not in board_member:
                error_message = {"error":"Reported user is not a member of board"}
                raise ValidationError(detail=error_message)

        return attrs
            


class CommentSerializer(serializers.ModelSerializer):
    author=UserDetailSerializer(read_only=True)
    class Meta:
        model=Comment
        fields='__all__'

    
    def validate(self, attrs):
        card=attrs.get('card')
        board_members=card.column.board.members.all()

        if self.context['request'].user not in board_members:
            error_message ={"error": "You are not authorized to comment. Should be board member."}
            raise ValidationError(detail=error_message)
        
        return attrs
    

