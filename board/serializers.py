from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError


from .models import *

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

class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model=Column
        fields='__all__'

    
    def commit_column_changes(self, start_value, end_value, nature_value, instance, validated_data):
        try:
            with transaction.atomic():

                for i in range(start_value,end_value,nature_value):
                    single_column=Column.objects.get(board=instance.board,order=i)
                    single_column.order=i+1
                    single_column.save()
                
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
                instance=self.commit_column_changes(recent_order,previous_order,1,instance,validated_data)

            elif previous_order>recent_order:
                instance=self.commit_column_changes(previous_order,recent_order,-1,instance,validated_data)

            return instance

        else:

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()

            return instance
            

        

class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model=Card
        fields='__all__'

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Comment
        fields='__all__'