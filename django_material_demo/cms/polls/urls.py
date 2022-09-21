from django.urls import include, path
from django.views.generic.base import RedirectView

from cms.polls import views

app_name = 'cms_polls'
urlpatterns = [
    path('', RedirectView.as_view(url='user/', permanent=True), name='index'),
    path('user/', include(views.UserViewSet().urls)),
    path("user/<int:pk>/password/",
        views.PasswordChangeView.as_view(),
        name="password_change"),
    path("user/<int:pk>/password/done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",),

    path('file/', include(views.FileViewSet().urls)),
    path('question/', include(views.QuestionViewSet().urls)),
    path('vote/', include(views.VoteViewSet().urls)),
]
