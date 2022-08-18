from django.contrib import admin

from .models import Choice, Question, User


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['question_text', 'total_vote_count']
        }),
        ('Date information', {
            'fields': [
                'pub_date',
                ('vote_start', 'vote_end'),
            ],
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
    inlines = [ChoiceInline]

    list_display = ['question_text', 'pub_date', 'vote_start',
                    'vote_end', 'total_vote_count', 'selection_bounds']
    list_filter = ['pub_date', 'vote_start', 'vote_end']
    search_fields = ['question_text']


admin.site.register(User)
admin.site.register(Question)
