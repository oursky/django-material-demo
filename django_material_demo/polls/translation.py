from modeltranslation.translator import TranslationOptions, register

from .models import Choice, Question


@register(Choice)
class ChoiceTranslationOptions(TranslationOptions):
    fields = ['choice_text']

@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ['question_text']
