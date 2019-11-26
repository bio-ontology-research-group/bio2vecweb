from django.shortcuts import render
from django.views.generic import ListView, DetailView
from events.models import Event

class EventsListView(ListView):

    model = Event
    template_name = 'events/list.html'

    def get_queryset(self, *args, **kwargs):
        queryset = super(EventsListView, self).get_queryset(
            *args, **kwargs)
        return queryset.order_by('-start_date')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/view.html'
