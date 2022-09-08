from django.urls import include, path
from django.views.generic.base import RedirectView

from . import admin_views, views

app_name = 'polls'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('<int:pk>/', views.QuestionView.as_view(), name='question'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),

    path('admin/', RedirectView.as_view(url='user/', permanent=True), name='index'),
    path('admin/user/', include(admin_views.UserViewSet().urls)),
    path("admin/user/<int:pk>/password/",
         admin_views.PasswordChangeView.as_view(),
         name="password_change"),
    path("admin/user/<int:pk>/password/done/",
         admin_views.PasswordChangeDoneView.as_view(),
         name="password_change_done",),

    path('admin/file/', include(admin_views.FileViewSet().urls)),
    path('admin/question/', include(admin_views.QuestionViewSet().urls)),
    path('admin/vote/', include(admin_views.VoteViewSet().urls)),
    path('admin/settings', admin_views.SettingsView.as_view(), name='settings'),
]
