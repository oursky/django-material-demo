from dataclasses import dataclass
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils import timezone


class File(models.Model):
    file_id = models.TextField()
    storage_loc = models.TextField('storage location')
    file_name = models.CharField(max_length=100)
    file_type = models.TextField()
    file_size = models.IntegerField()

    def __str__(self):
        return self.file_name


class User(models.Model):
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Group(models.TextChoices):
        DEFAULT = 'DEFAULT', 'default'
        SUBS = 'SUBS', 'subscriber'
        SA = 'SA', 'super admin'

    group = models.CharField(
        max_length=10, choices=Group.choices, default=Group.DEFAULT)

    subs_start = models.DateField(
        'subscription start date', null=True, blank=True)
    subs_expire = models.DateField(
        'subscription expire date', null=True, blank=True)

    followed_users = models.ManyToManyField(
        'User', blank=True, symmetrical=False,
        through='UserFollower',
        through_fields=('follower', 'followed_user'))

    def __str__(self):
        return self.account.username

    @property
    def name(self):
        return self.account.username

    @property
    def email(self):
        return self.account.email

    def followers_list(self):
        users = UserFollower.objects.filter(followed_user=self)
        users = users.order_by('-ordering', 'follower__account__username')
        return [x.follower.name for x in users]


class UserFollower(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_follows')
    followed_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_followed')
    ordering = models.FloatField(default=0)
    enable_email_notify = models.BooleanField(default=False)
    notify_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return str(self.follower) + ' → ' + str(self.followed_user)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    total_vote_count = models.IntegerField(default=0)

    thumbnail = models.ForeignKey(
        File, on_delete=models.CASCADE, null=True, blank=True)

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='question_creates',
        null=True, blank=True)
    show_creator = models.BooleanField(default=False)

    followers = models.ManyToManyField(
        User, related_name='question_follows',
        through='QuestionFollower', blank=True)

    pub_date = models.DateTimeField('date published', default=timezone.now)
    vote_start = models.DateTimeField(
        'vote start date', default=timezone.now)
    vote_end = models.DateTimeField(
        'vote end date', null=True, blank=True)

    class ShowVote(models.TextChoices):
        VOTE = 'VOTE', 'after vote'
        END = 'END', 'after voting ends'
        NEVER = 'NEVER', 'never'

    show_vote = models.CharField(
        max_length=10, choices=ShowVote.choices, default=ShowVote.END)
    min_selection = models.IntegerField(default=1)
    max_selection = models.IntegerField(null=True, blank=True)
    has_max_vote_count = models.BooleanField(default=False)
    max_vote_count = models.IntegerField(null=True, blank=True)
    allow_custom = models.BooleanField('allow custom votes', default=False)

    def __str__(self):
        return self.question_text

    @admin.display()
    def selection_bounds(self):
        if self.min_selection == self.max_selection:
            return self.min_selection
        else:
            return '%(min)s - %(max)s' % {
                'min': self.min_selection or 1,
                'max': self.max_selection or 'unbounded'}

    def choice_list(self):
        choices = Choice.objects.filter(question=self)
        choices = choices.order_by('choice_text')
        return [choice.choice_text for choice in choices]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    is_custom = models.BooleanField(default=False)
    choice = models.ForeignKey(
        Choice, on_delete=models.CASCADE, null=True, blank=True)
    custom_choice_text = models.CharField(
        max_length=200, null=True, blank=True)

    def __str__(self):
        return '#%(id)s (%(question)s)' % {
            'question': str(self.question),
            'id': str(self.pk)[:8]}

    def choice_text(self):
        if self.is_custom:
            return self.custom_choice_text
        else:
            return str(self.choice)


class Attachment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    file = models.OneToOneField(File, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.file)


class QuestionFollower(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    ordering = models.FloatField(default=0)
    enable_email_notify = models.BooleanField(default=False)
    notify_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return str(self.follower) + ' → ' + str(self.question)


class Settings(models.Model):
    managed = False

    primary_color = models.TextField()
    primary_color_light = models.TextField()
    primary_color_dark = models.TextField()
    secondary_color = models.TextField()
    secondary_color_light = models.TextField()
    success_color = models.TextField()
    error_color = models.TextField()
    link_color = models.TextField()

    def __init__(self, *args, **kwargs):
        self.session = kwargs['session']
        del kwargs['session']
        super().__init__(*args, **kwargs)
        self.load()

    def load(self):
        self.primary_color = self.session.get('settings:--primary-color') or '#424242'
        self.primary_color_light = self.session.get('settings:--primary-color-light') or '#686868'
        self.primary_color_dark = self.session.get('settings:--primary-color-dark') or '#1c1c1c'
        self.secondary_color = self.session.get('settings:--secondary-color') or '#37474f'
        self.secondary_color_light = self.session.get('settings:--secondary-color-light') or '#56707c'
        self.success_color = self.session.get('settings:--sucess-color') or '#607d8b'
        self.error_color = self.session.get('settings:--error-color') or '#f44336'
        self.link_color = self.session.get('settings:--link-color') or '#039be5'

    def save(self):
        self.session['settings:--primary-color'] = self.primary_color
        self.session['settings:--primary-color-light'] = self.primary_color_light
        self.session['settings:--primary-color-dark'] = self.primary_color_dark
        self.session['settings:--secondary-color'] = self.secondary_color
        self.session['settings:--secondary-color-light'] = self.secondary_color_light
        self.session['settings:--sucess-color'] = self.success_color
        self.session['settings:--error-color'] = self.error_color
        self.session['settings:--link-color'] = self.link_color
