# Generated by Django 4.1 on 2022-09-23 09:52

import io

from django.core.files import File as DjangoFile
from django.core.files.storage import get_storage_class
from django.db import migrations


STORAGE = get_storage_class()()
# Should match with same variable in migration 0012
DUMMY_FILE_NAME = 'DUMMY_FILE_NAME'


def migrate_files(apps, schema_editor):
    question_model = apps.get_model('polls', 'Question')
    attachment_model = apps.get_model('polls', 'Attachment')

    for question in question_model.objects.all():
        if question.thumbnail:
            file = question.thumbnail_copy
            question.thumbnail = file.file_name
            question.save()
    for attachment in attachment_model.objects.all():
        file = attachment.file_copy
        attachment.file = file.file_name
        attachment.save()
    pass


def create_dummy_file(file_instance):
    return DjangoFile(io.StringIO(), name=str(file_instance.pk))


def migrate_back_files(apps, schema_editor):
    file_model = apps.get_model('polls', 'File')
    question_model = apps.get_model('polls', 'Question')
    attachment_model = apps.get_model('polls', 'Attachment')

    file_data_default = {
        'file_id': 'DEFAULT_0123456789abcdef',
        'file_size': '123456',
        'storage_loc': 'local_storage',
        'file_type': 'application/octet-stream'
    }
    for question in question_model.objects.all():
        file_name = question.thumbnail or DUMMY_FILE_NAME
        file = file_model.objects.create(
            file_name=file_name, **file_data_default)
        question.thumbnail_copy = file
        question.thumbnail = create_dummy_file(file)
        question.save()
    for attachment in attachment_model.objects.all():
        file = file_model.objects.create(
            file_name=attachment.file, **file_data_default)
        attachment.file_copy = file
        attachment.file = create_dummy_file(file)
        attachment.save()
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0013_alter_attachment_file_alter_question_thumbnail'),
    ]

    operations = [
        migrations.RunPython(migrate_files, migrate_back_files),
        migrations.RemoveField(
            model_name='attachment',
            name='file_copy',
        ),
        migrations.RemoveField(
            model_name='question',
            name='thumbnail_copy',
        ),
        migrations.DeleteModel(
            name='File',
        ),
    ]
