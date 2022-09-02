from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Attachment, Choice, File, Question, User, UserFollower, Vote


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    readonly_fields = [
        'file_id',
        'storage_loc',
        'file_name',
        'file_type',
        'file_size',
    ]

    list_display = ['file_name', 'file_type', 'file_size', 'storage_loc']
    list_filter = ['file_type', 'storage_loc']
    search_fields = ['file_name']


class FollowedQuestion(admin.TabularInline):
    model = Question.followers.through
    extra = 1
    verbose_name = 'followed question'
    exclude = ['ordering']


class FollowedUser(admin.TabularInline):
    model = UserFollower
    fk_name = 'follower'
    extra = 1
    verbose_name = 'followed user'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = [
        'account',
        'group',
        ('subs_start', 'subs_expire'),
    ]
    inlines = [FollowedQuestion, FollowedUser]
    radio_fields = {"group": admin.HORIZONTAL}

    list_display = ['account', 'group', 'subs_start', 'subs_expire']
    list_filter = ['group']
    search_fields = ['account']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


class FollowerInline(admin.TabularInline):
    model = Question.followers.through
    extra = 1
    verbose_name = 'follower'
    fields = ['follower', 'ordering']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [
                'question_text',
                'total_vote_count',
                'thumbnail',
                ('creator', 'show_creator'),
            ]
        }),
        ('Date information', {
            'fields': ['pub_date', ('vote_start', 'vote_end')],
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
    inlines = [ChoiceInline, AttachmentInline, FollowerInline]

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

    list_display = ['timestamp', 'question', 'choice_text', 'is_custom']
    list_filter = ['is_custom']
    search_fields = ['question']
