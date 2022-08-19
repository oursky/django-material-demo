from django.contrib import admin

from .models import Attachment, Choice, File, Question, User, Vote


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'file_size', 'storage_loc']
    list_filter = ['file_type', 'storage_loc']
    search_fields = ['file_name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'subs_start', 'subs_expire']
    list_filter = ['group']
    search_fields = ['name']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['question_text', 'total_vote_count']
        }),
        ('User related', {
            'fields': [('creator', 'show_creator'), 'followers']
        }),
        ('Date information', {
            'fields': ['pub_date', ('vote_start', 'vote_end'), ],
            'classes': ['collapse'],
        }),
        ('Vote restrictions', {
            'fields': [
                'show_vote',
                ('has_max_vote_count', 'max_vote_count'),
                ('min_selection', 'max_selection'),
                'allow_custom',
            ],
            'classes': ['collapse'],
        })]
    inlines = [ChoiceInline, AttachmentInline]

    list_display = ['question_text', 'pub_date', 'vote_start',
                    'vote_end', 'total_vote_count', 'selection_bounds']
    list_filter = ['pub_date', 'vote_start', 'vote_end']
    search_fields = ['question_text']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    fields = [
        'question',
        'timestamp',
        'is_custom',
        'choice',
        'custom_choice_text',
    ]
    list_display = ['question', 'choice_text', 'is_custom', 'timestamp']
    list_filter = ['is_custom']
    search_fields = ['question']
