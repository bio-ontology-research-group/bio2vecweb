"""bio2vecweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf import settings

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html')),
    path('admin/', admin.site.urls),
    path('bio2vec/', include('bio2vec.urls')),
    path('accounts/', include('accounts.urls')),
    path('partners/', include('partners.urls')),
    path('news/', include('news.urls')),
    path('events/', include('events.urls')),
    path('manage/', include('bio2vecweb.manage_urls')),
    path('api/', include('bio2vecweb.api_urls')),
    path('about',
         TemplateView.as_view(template_name='about.html'), name='about'),
    path('publications',
         TemplateView.as_view(template_name='publications.html'),
         name='publications'),
    path('contacts',
         TemplateView.as_view(template_name='contacts.html'),
         name='contacts'),
    path('healthcheck', TemplateView.as_view(template_name='health.html')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
