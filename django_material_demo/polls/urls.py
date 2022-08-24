from django.contrib import admin
from django.urls import include, path

from . import views, admin_views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),

    path('admin/file/', include(admin_views.FileViewSet().urls)),
    path('admin/user/', include(admin_views.UserViewSet().urls)),
    path('admin/question/', include(admin_views.QuestionViewSet().urls)),
    path('admin/vote/', include(admin_views.VoteViewSet().urls)),
]
