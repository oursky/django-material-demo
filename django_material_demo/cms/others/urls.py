from django.urls import path

from .views import CustomizedComponentView

app_name = 'others'
urlpatterns = [
    path('', CustomizedComponentView.as_view(), name='index'),
]
