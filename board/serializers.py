from rest_framework import serializers
from .models import *

class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model=Board
        fields='__all__'

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model=Tag
        fields='__all__'

class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model=Column
        fields='__all__'

class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model=Card
        fields='__all__'

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Comment
        fields='__all__'