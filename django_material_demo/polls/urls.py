from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

from . import views, admin_views

app_name = 'polls'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('<int:pk>/', views.QuestionView.as_view(), name='question'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),

    path('admin/', RedirectView.as_view(url='user/', permanent=True), name='index'),
    path('admin/user/', include(admin_views.UserViewSet().urls)),
    path('admin/file/', include(admin_views.FileViewSet().urls)),
    path('admin/question/', include(admin_views.QuestionViewSet().urls)),
    path('admin/vote/', include(admin_views.VoteViewSet().urls)),
]
