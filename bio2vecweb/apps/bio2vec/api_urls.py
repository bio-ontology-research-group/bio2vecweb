from django.urls import include, path
from django.contrib.auth.decorators import login_required
from bio2vec import api_views

urlpatterns = [
    path('mostsimilar',
         api_views.MostSimilarAPIView.as_view(),
         name='api-bio2vec-mostsimilar'),
    path('search',
         api_views.SearchEntitiesAPIView.as_view(),
         name='api-bio2vec-search'),
]
