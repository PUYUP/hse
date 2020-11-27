import os
from django.core.exceptions import ObjectDoesNotExist

from django.db import transaction

from rest_framework import serializers

from utils.generals import get_model

Chapter = get_model('training', 'Chapter')
Course = get_model('training', 'Course')
Material = get_model('training', 'Material')


def handle_upload_material(instance, file):
    if instance and file:
        name, ext = os.path.splitext(file.name)

        instance.media.save('%s%s' % (name, ext), file, save=False)
        instance.save(update_fields=['media'])


class ChapterSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='uuid', queryset=Course.objects.all())

    class Meta:
        model = Chapter
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        file = request.FILES.get('file')
        course = validated_data.get('course')
        instance = Chapter.objects.create(**validated_data)

        if file:
            material = Material.objects.create(course=course, chapter=instance)
            handle_upload_material(material, file)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get('request')
        file = request.FILES.get('file')

        for key, value in validated_data.items():
            if hasattr(instance, key):
                old_value = getattr(instance, key, None)
                if old_value != value:
                    setattr(instance, key, value)

        if file:
            try:
                material = instance.material.first()
            except ObjectDoesNotExist:
                material = Material.objects.create(course=instance.course, chapter=instance)
                
            handle_upload_material(material, file)

        instance.save()
        return instance
