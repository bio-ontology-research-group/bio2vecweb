from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse
from partners.models import ResearchGroup, Member


class ResearchGroupListView(ListView):
    model = ResearchGroup
    template_name = 'partners/groups_list.html'

    def get_queryset(self, *args, **kwargs):
        queryset = super(ResearchGroupListView, self).get_queryset(
            *args, **kwargs)
        return queryset.order_by('order')


class MemberDetailView(DetailView):
    model = Member
    template_name = 'partners/member.html'
