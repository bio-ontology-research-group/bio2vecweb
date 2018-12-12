from django.urls import include, path
from django.contrib.auth.decorators import login_required
from bio2vec import manage_views as views

urlpatterns = [
    path('dataset/',
        login_required(views.MyDatasetListView.as_view()),
        name='list-my-datasets'),
    path('dataset/create/',
        login_required(views.DatasetCreateView.as_view()),
        name='create-dataset'),
    path('dataset/edit/<int:pk>',
        login_required(views.DatasetUpdateView.as_view()),
        name='edit-dataset'),
]
