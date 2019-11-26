from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse
from bio2vec.models import Dataset, Distribution
from bio2vec.forms import DatasetForm, DistributionForm
from bio2vecweb.mixins import FormRequestMixin, ActionMixin
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib import messages
from bio2vec.mixins import DatasetMixin


class MyDatasetListView(ActionMixin, ListView):

    model = Dataset
    template_name = 'bio2vec/manage/list_datasets.html'

    def get_queryset(self, *args, **kwargs):
        return self.request.user.created_datasets.all()

    def get_success_url(self):
        return reverse('list_datasets')

    
    
class DatasetCreateView(FormRequestMixin, CreateView):

    model = Dataset
    form_class = DatasetForm
    template_name = 'bio2vec/manage/edit_dataset.html'

    def get_success_url(self):
        kwargs = {'dataset_pk': self.object.pk}
        return reverse('create-distrib', kwargs=kwargs)


class DatasetUpdateView(FormRequestMixin, UpdateView):

    model = Dataset
    form_class = DatasetForm
    template_name = 'bio2vec/manage/edit_dataset.html'

    def get_success_url(self):
        kwargs = {'dataset_pk': self.object.pk}
        return reverse('create-distrib', kwargs=kwargs)


class DistributionCreateView(DatasetMixin, FormRequestMixin, CreateView):

    model = Distribution
    form_class = DistributionForm
    template_name = 'bio2vec/manage/edit_distrib.html'

    def get_success_url(self):
        kwargs = {'pk': self.object.pk, 'dataset_pk': self.object.dataset.pk}
        return reverse('edit-distrib', kwargs=kwargs)


class DistributionUpdateView(DatasetMixin, FormRequestMixin, UpdateView):

    model = Distribution
    form_class = DistributionForm
    template_name = 'bio2vec/manage/edit_distrib.html'

    def get_success_url(self):
        kwargs = {'pk': self.object.pk, 'dataset_pk': self.object.dataset.pk}
        return reverse('edit-distrib', kwargs=kwargs)


class DistributionDeleteView(DeleteView):

    model = Distribution
    template_name = 'bio2vec/manage/delete_distrib.html'

    def get_success_url(self):
        kwargs = {'dataset_pk': self.object.dataset.pk }
        return reverse('create-distrib', kwargs=kwargs)
