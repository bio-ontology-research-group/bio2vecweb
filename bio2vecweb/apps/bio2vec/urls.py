from django.urls import include, path
from django.contrib.auth.decorators import login_required
from bio2vec import views

urlpatterns = [
    path('',
        views.DatasetsListView.as_view(),
        name='list-datasets'),
    path('details/<int:pk>',
        views.DatasetDetailView.as_view(),
        name='view-dataset'),
    path('sparql/<int:pk>',
        views.DatasetSPARQLView.as_view(),
        name='sparql-dataset'),
]
