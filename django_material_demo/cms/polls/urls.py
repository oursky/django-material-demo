from django.urls import include, path
from django.views.generic.base import RedirectView

from .views import question, user, vote

urlpatterns = [
    path('', RedirectView.as_view(url='user/', permanent=True), name='index'),
    path('user/', include(user.UserViewSet().urls)),
    path("user/<int:pk>/password/",
         user.PasswordChangeView.as_view(),
         name="password_change"),
    path("user/<int:pk>/password/done/",
         user.PasswordChangeDoneView.as_view(),
         name="password_change_done",),

    path('question/', include(question.QuestionViewSet().urls)),
    path('vote/', include(vote.VoteViewSet().urls)),
]
