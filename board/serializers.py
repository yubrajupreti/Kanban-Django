
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


from user.serializers import UserDetailSerializer
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
            error_message = f'Tag with {tag_name} already exists.'
            raise ValidationError(detail=error_message)
        return attrs

class ColumnSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context and self.context['view'].action in ['create']:
            self.fields.pop('order', None)

    class Meta:
        model=Column
        fields='__all__'

    
    def commit_column_changes(self, start_value, end_value, nature_value,condition_value, instance, validated_data):
        try:
            with transaction.atomic():
                # increase if the previous order was greater than recent changing order and vice versa
                start_value=start_value+1 if condition_value==1 else start_value-1

                for i in range(start_value,end_value,nature_value):

                    # decrease by 1, if the previous order was greater than recent changing order and vice versa
                    order_value=i-1 if condition_value==1 else i+1
                    single_column=Column.objects.get(board=instance.board,order=order_value)
                    single_column.order=i
                    single_column.save()

                # update actual instance
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
        
                instance.save()
        
            return instance
        
        except Exception as e:
            transaction.rollback()
            error_message = "An error occurred during the update process."
            raise ValidationError(detail=error_message)

    
    def update(self, instance, validated_data):

        if 'order' in validated_data:
            recent_order=validated_data.get('order')
            previous_order=instance.order
            if previous_order>recent_order:
                instance=self.commit_column_changes(
                    previous_order,recent_order,-1,1,instance,validated_data
                    )

            elif previous_order<recent_order:
                # 1 indicate the nature of loop
                # 0 indicate the order condition
                instance=self.commit_column_changes(
                    previous_order,recent_order,1,0,instance,validated_data
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
class CardSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context and self.context['view'].action in ['create']:
            self.fields.pop('order', None)

    class Meta:
        model=Card
        fields='__all__'

    def commit_card_changes(self, start_value, end_value, nature_value,condition_value, instance, validated_data):
        try:
            with transaction.atomic():
                # increase if the previous order was greater than recent changing order and vice versa
                start_value=start_value+1 if condition_value==1 else start_value-1
                for i in range(start_value,end_value,nature_value):

                    # decrease by 1, if the previous order was greater than recent changing order and vice versa
                    order_value=i-1 if condition_value==1 else i+1
                    single_column=Card.objects.get(column=instance.column,order=order_value)
                    single_column.order=i
                    single_column.save()

                # update actual instance
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
        
                instance.save()
        
            return instance
        
        except Exception as e:
            transaction.rollback()
            error_message = "An error occurred during the update process."
            raise ValidationError(detail=error_message)

    
    def update(self, instance, validated_data):

        if 'order' in validated_data:
            recent_order=validated_data.get('order')
            previous_order=instance.order
            if previous_order>recent_order:
                instance=self.commit_card_changes(
                    previous_order,recent_order,-1,1,instance,validated_data
                    )

            elif previous_order<recent_order:
                # 1 indicate the nature of loop
                # 0 indicate the order condition
                instance=self.commit_card_changes(
                    previous_order,recent_order,1,0,instance,validated_data
                    )

            return instance

        else:

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()

            return instance
        
    def validate(self, attrs):
        assigned=attrs.get('assignees','')
        reporter=attrs.get('reporter','')
        column=attrs.get('column')
        board_member=column.board.members.all()

        if assigned:
            if assigned.id not in board_member:
                error_message = "Assigned user is not a member of board"
                raise ValidationError(detail=error_message)
        if reporter:
            if reporter.id not in board_member:
                error_message = "Assigned user is not a member of board"
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
            error_message = "You are not authorized to comment. Should be board member."
            raise ValidationError(detail=error_message)
        
        return attrs
    

