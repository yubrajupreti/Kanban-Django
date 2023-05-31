from django.db import transaction

from rest_framework.exceptions import ValidationError


from .models import *


class CardSorting:
    
    def commit_card_column_change(self,previous_column,recent_column,recent_order,instance,validated_data):
        try:
            with transaction.atomic():

                # sorting the previous column
                previous_column_card=Card.objects.filter(column=previous_column)
                last_index=previous_column_card.count()

                # initial value is increase by 1 as card at greater index should be decrease by 1
                for i in range(instance.order+1,last_index+1):
                    single_card=previous_column_card.get(order=i)
                    single_card.order-=1
                    single_card.save()

                # sorting the current column of card
                current_column_card=Card.objects.filter(column=recent_column)
                current_last_index=current_column_card.count()
                
                # card has been added so the final value should be decrease by 1 as it is a reverse loop
                for i in range(current_last_index,recent_order-1,-1):
                    single_card=current_column_card.get(order=i)
                    single_card.order+=1
                    single_card.save()

                # update actual instance
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
        
                instance.save()
        
            return instance
        except Exception as e:
            transaction.rollback()
            error_message = {"error":"An error occurred during the update process."}
            raise ValidationError(detail=error_message)
        
    def commit_order_changes(self, start_value, end_value, nature_value,condition_value, instance, validated_data,order_for):
        try:
            with transaction.atomic():
                # increase if the previous order was greater than recent changing order and vice versa
                start_value=start_value+1 if condition_value==1 else start_value-1
                for i in range(start_value,end_value,nature_value):

                    # decrease by 1, if the previous order was greater than recent changing order and vice versa
                    order_value=i-1 if condition_value==1 else i+1
                    if order_for==1:
                        single_column=Card.objects.get(column=instance.column,order=order_value)
                    else:
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
            error_message = {"error":"An error occurred during the update process."}
            raise ValidationError(detail=error_message)