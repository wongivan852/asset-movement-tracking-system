from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q

from .models import Movement, StockTake, MovementAcknowledgement
from assets.models import Asset


class MovementListView(LoginRequiredMixin, ListView):
    model = Movement
    template_name = 'movements/list.html'
    context_object_name = 'movements'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Movement.objects.select_related(
            'asset', 'from_location', 'to_location', 'initiated_by'
        ).order_by('-created_at')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        asset = self.request.GET.get('asset')
        if asset:
            queryset = queryset.filter(asset_id=asset)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Movement.STATUS_CHOICES
        return context


class MovementDetailView(LoginRequiredMixin, DetailView):
    model = Movement
    template_name = 'movements/detail.html'
    context_object_name = 'movement'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acknowledgements'] = self.object.acknowledgements.select_related(
            'acknowledged_by'
        ).order_by('acknowledged_at')
        return context


class MovementCreateView(LoginRequiredMixin, CreateView):
    model = Movement
    template_name = 'movements/form.html'
    fields = ['asset', 'from_location', 'to_location', 'movement_type', 
              'reason', 'notes', 'expected_arrival']
    
    def form_valid(self, form):
        form.instance.initiated_by = self.request.user
        messages.success(self.request, 'Movement created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('movements:detail', kwargs={'pk': self.object.pk})


class MovementUpdateView(LoginRequiredMixin, UpdateView):
    model = Movement
    template_name = 'movements/form.html'
    fields = ['movement_type', 'reason', 'notes', 'expected_arrival', 'status']
    
    def form_valid(self, form):
        messages.success(self.request, 'Movement updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('movements:detail', kwargs={'pk': self.object.pk})


class StockTakeListView(LoginRequiredMixin, ListView):
    model = StockTake
    template_name = 'movements/stock_takes.html'
    context_object_name = 'stock_takes'
    paginate_by = 20
    
    def get_queryset(self):
        return StockTake.objects.select_related(
            'location', 'performed_by'
        ).order_by('-created_at')


class StockTakeDetailView(LoginRequiredMixin, DetailView):
    model = StockTake
    template_name = 'movements/stock_take_detail.html'
    context_object_name = 'stock_take'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related(
            'asset'
        ).order_by('asset__asset_id')
        return context


class StockTakeCreateView(LoginRequiredMixin, CreateView):
    model = StockTake
    template_name = 'movements/stock_take_form.html'
    fields = ['location', 'notes']
    
    def form_valid(self, form):
        form.instance.performed_by = self.request.user
        messages.success(self.request, 'Stock take created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('movements:stock_take_detail', kwargs={'pk': self.object.pk})


class AcknowledgeMovementView(LoginRequiredMixin, UpdateView):
    model = Movement
    template_name = 'movements/acknowledge.html'
    fields = []
    
    def form_valid(self, form):
        movement = self.get_object()
        MovementAcknowledgement.objects.create(
            movement=movement,
            acknowledged_by=self.request.user,
            notes=self.request.POST.get('notes', '')
        )
        movement.status = 'completed'
        movement.save()
        messages.success(self.request, 'Movement acknowledged successfully!')
        return redirect('movements:detail', pk=movement.pk)
