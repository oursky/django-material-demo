from django.urls import include, path
from material.frontend import urls as frontend_urls

urlpatterns = [
    path('', include(frontend_urls)),
]
