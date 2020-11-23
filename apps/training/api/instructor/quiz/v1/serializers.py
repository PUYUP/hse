from django.db import transaction
from django.http import request

from rest_framework import serializers

from utils.generals import get_model

Question = get_model('training', 'Question')


class QuestionListSerializer(serializers.ListSerializer):
    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get('request', {})
        position = request.get('position')
        course_uuid = request.get('course_uuid')

        # Maps for uuid->instance and uuid->data item.
        obj_mapping = {obj.uuid: obj for obj in instance}
        data_mapping = {item.get('uuid', index): item for index, item in enumerate(validated_data)}

        # Perform creations and updates.
        ret = []
        for obj_uuid, data in data_mapping.items():
            obj = obj_mapping.get(obj_uuid, None)

            if obj is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(obj, data))

        # Perform deletions.
        for obj_uuid, obj in obj_mapping.items():
            if obj_uuid not in data_mapping:
                obj.delete()

        return ret


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        list_serializer_class = QuestionListSerializer
