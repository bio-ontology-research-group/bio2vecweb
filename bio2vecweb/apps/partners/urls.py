from django.urls import include, path
from django.contrib.auth.decorators import login_required
from partners import views

urlpatterns = [
    path('',
        views.ResearchGroupListView.as_view(),
        name='list-partners'),
    path('details/<int:pk>',
        views.MemberDetailView.as_view(),
        name='view-member'),
]
