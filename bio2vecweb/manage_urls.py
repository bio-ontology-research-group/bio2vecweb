"""bio2vecweb Management URL Configuration
"""
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path('bio2vec/', include('bio2vec.manage_urls')),
]
