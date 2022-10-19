# Generated by Django 4.1 on 2022-10-12 09:12

from django.db import migrations, models


def add_translations(apps, schema_editor):
    choice = apps.get_model('polls', 'choice')
    choice.objects.update(choice_text_en=models.F('choice_text'))
    question = apps.get_model('polls', 'question')
    question.objects.update(question_text_en=models.F('question_text'))


def revert_translations(apps, schema_editor):
    choice = apps.get_model('polls', 'choice')
    choice.objects.update(choice_text=models.F('choice_text_en'))
    question = apps.get_model('polls', 'question')
    question.objects.update(question_text=models.F('question_text_en'))


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0014_remove_file_model_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='choice_text_en',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='choice',
            name='choice_text_zh_hant',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='question_text_en',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='question_text_zh_hant',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.RunPython(add_translations, revert_translations),
    ]
