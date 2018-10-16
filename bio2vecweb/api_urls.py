"""bio2vecweb API URL Configuration
"""
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path('bio2vec/', include('bio2vec.api_urls')),
]
