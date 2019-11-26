from bio2vec.models import Dataset
from django.http import Http404


class DatasetMixin(object):

    def get_dataset(self, *args, **kwargs):
        try:
            dataset_pk = self.kwargs.get('dataset_pk')
            self.dataset = Dataset.objects.get(pk=dataset_pk)
        except Exception as e:
            raise Http404
        
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(DatasetMixin, self).get_form_kwargs(*args, **kwargs)
        kwargs['dataset'] = self.dataset
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super(DatasetMixin, self).get_context_data(
            *args, **kwargs)
        context['dataset'] = self.dataset
        return context

    def get(self, request, *args, **kwargs):
        self.get_dataset()
        return super(DatasetMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_dataset()
        return super(DatasetMixin, self).post(request, *args, **kwargs)
