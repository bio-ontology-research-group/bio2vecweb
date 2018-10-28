from django.views.generic import ListView, DetailView
from bio2vec.models import Dataset

class DatasetsListView(ListView):

    model = Dataset
    template_name = 'bio2vec/list.html'

    def get_queryset(self, *args, **kwargs):
        queryset = super(DatasetsListView, self).get_queryset(
            *args, **kwargs)
        return queryset


class DatasetDetailView(DetailView):
    model = Dataset
    template_name = 'bio2vec/view.html'
