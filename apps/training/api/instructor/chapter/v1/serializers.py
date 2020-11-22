import os

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

        material = Material.objects.create(course=course, chapter=instance)
        if file:
            handle_upload_material(material, file)

        return instance
