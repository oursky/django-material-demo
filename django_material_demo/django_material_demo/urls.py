"""django_material_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path
from django.views.generic.base import RedirectView
from material.frontend import urls as frontend_urls
from polls.forms import EmailLoginForm

urlpatterns = [
    path('', RedirectView.as_view(url='polls/', permanent=True), name='index'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    # Override login page from Frontend
    path('cms/accounts/login/', LoginView.as_view(
        authentication_form=EmailLoginForm),
        name="login"
    ),
    # reserve `polls` namespace for polls urls in CMS
    path('polls/', include('polls.urls', namespace='app_polls')),
    path('cms/', include(frontend_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
