from django.urls import include, path
from django.contrib.auth.decorators import login_required
from events import views

urlpatterns = [
    path('',
        views.EventsListView.as_view(),
        name='list-events'),
    path('details/<int:pk>',
        views.EventDetailView.as_view(),
        name='view-event'),
]
