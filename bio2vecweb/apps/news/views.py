from django.shortcuts import render
from django.views.generic import ListView, DetailView
from news.models import News

class NewsListView(ListView):

    model = News
    template_name = 'news/list.html'

    def get_queryset(self, *args, **kwargs):
        queryset = super(NewsListView, self).get_queryset(
            *args, **kwargs)
        return queryset.order_by('-news_date')


class NewsDetailView(DetailView):
    model = News
    template_name = 'news/view.html'
