from rest_framework import serializers

from utils.generals import get_model

Category = get_model('training', 'Category')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['uuid', 'label']
