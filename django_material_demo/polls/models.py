from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils import timezone


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

    class Meta:
        ordering = ['account__username', 'id']

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

    class Meta:
        ordering = ['-ordering', 'id']

    def __str__(self):
        return str(self.follower) + ' → ' + str(self.followed_user)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    total_vote_count = models.IntegerField(default=0)

    thumbnail = models.FileField(blank=True, null=True)

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

    class Meta:
        ordering = ['question_text', 'id']

    def __str__(self):
        return self.question_text

    class Meta:
        ordering = ['question_text']

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

    class Meta:
        ordering = ['choice_text', 'id']

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

    class Meta:
        ordering = ['-timestamp', 'id']

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
    file = models.FileField(blank=True, null=True)

    class Meta:
        ordering = ['file', 'id']

    def __str__(self):
        return str(self.file)


class QuestionFollower(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    ordering = models.FloatField(default=0)
    enable_email_notify = models.BooleanField(default=False)
    notify_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['-ordering', 'question', 'id']

    def __str__(self):
        return str(self.follower) + ' → ' + str(self.question)
