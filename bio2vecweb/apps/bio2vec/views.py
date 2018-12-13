from django.views.generic import ListView, DetailView
from bio2vec.models import Dataset
import requests
from django.conf import settings
from django.http import Http404
import json

BIO2VEC_API_URL = getattr(
    settings, 'BIO2VEC_API_URL', 'http://localhost:8000/api/bio2vec')

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

    def get_context_data(self, *args, **kwargs):
        context = super(DatasetDetailView, self).get_context_data(*args, **kwargs)
        dataset = self.get_object()
        iri = self.request.GET.get('iri', None)

        entity = {'id': iri}
        similars = {}
        if iri is not None:
            params = {
                'dataset': dataset.name, 'id': iri, 'format': 'json', 'size':100}
            r = requests.get(
                BIO2VEC_API_URL + '/mostsimilar', params=params)
        else:
            params = {
                'dataset': dataset.name, 'format': 'json', 'size':100}
            r = requests.get(
                BIO2VEC_API_URL + '/entities', params=params)
        try:
            res = r.json()
            if iri is not None and iri in res['result']:
                similars = list(map(lambda x: x['_source'], res['result'][iri]))
            else:
                similars = list(map(lambda x: x['_source'], res['result']))
            print(BIO2VEC_API_URL, res)
            entity = similars[0]
        except Exception as e:
            print(e)

        for key in entity:
            if isinstance(entity[key], list):
                entity[key] = ', '.join(entity[key])
        context['entity'] = entity
        context['similars'] = similars
        similars_json = json.dumps(similars)
        context['similars_json'] = similars_json
        return context


class DatasetSPARQLView(DetailView):
    model = Dataset
    template_name = 'bio2vec/sparql.html'

    def get_context_data(self, *args, **kwargs):
        context = super(DatasetSPARQLView, self).get_context_data(*args, **kwargs)
        dataset = self.get_object()
        iri = self.request.GET.get('iri', None)
        context['iri'] = iri
        return context
