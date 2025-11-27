from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count

from .models import Location


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'locations/list.html'
    context_object_name = 'locations'
    
    def get_queryset(self):
        return Location.objects.annotate(
            asset_count=Count('assets')
        ).order_by('name')


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = 'locations/detail.html'
    context_object_name = 'location'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assets'] = self.object.assets.select_related(
            'category', 'responsible_person'
        ).order_by('asset_id')
        context['recent_movements'] = self.object.incoming_movements.select_related(
            'asset', 'from_location', 'initiated_by'
        ).order_by('-created_at')[:10]
        return context


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    template_name = 'locations/form.html'
    fields = ['name', 'code', 'address', 'city', 'country', 'contact_phone', 
              'contact_email', 'responsible_person']
    
    def form_valid(self, form):
        messages.success(self.request, f'Location {form.instance.name} created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('locations:detail', kwargs={'pk': self.object.pk})


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    template_name = 'locations/form.html'
    fields = ['name', 'code', 'address', 'city', 'country', 'contact_phone', 
              'contact_email', 'responsible_person', 'is_active']
    
    def form_valid(self, form):
        messages.success(self.request, f'Location {form.instance.name} updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('locations:detail', kwargs={'pk': self.object.pk})


class LocationAssetsView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = 'locations/assets.html'
    context_object_name = 'location'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assets'] = self.object.assets.select_related(
            'category', 'responsible_person'
        ).order_by('asset_id')
        return context
