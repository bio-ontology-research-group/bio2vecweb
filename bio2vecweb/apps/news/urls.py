from django.urls import include, path
from django.contrib.auth.decorators import login_required
from news import views

urlpatterns = [
    path('',
        views.NewsListView.as_view(),
        name='list-news'),
    path('details/<int:pk>',
        views.NewsDetailView.as_view(),
        name='view-news'),
]
