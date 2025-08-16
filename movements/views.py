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
        try:
            context['acknowledgement'] = self.object.acknowledgement
        except MovementAcknowledgement.DoesNotExist:
            context['acknowledgement'] = None
        return context


class MovementCreateView(LoginRequiredMixin, CreateView):
    model = Movement
    template_name = 'movements/form.html'
    fields = ['asset', 'from_location', 'to_location', 'reason', 'notes', 'expected_arrival_date', 'priority']
    
    def form_valid(self, form):
        form.instance.initiated_by = self.request.user
        messages.success(self.request, 'Movement created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('movements:detail', kwargs={'pk': self.object.pk})


class MovementUpdateView(LoginRequiredMixin, UpdateView):
    model = Movement
    template_name = 'movements/form.html'
    fields = ['reason', 'notes', 'expected_arrival_date', 'priority', 'status']
    
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
            'location', 'conducted_by'
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
        form.instance.conducted_by = self.request.user
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


class CancelMovementView(LoginRequiredMixin, UpdateView):
    model = Movement
    template_name = 'movements/cancel.html'
    fields = []
    
    def form_valid(self, form):
        movement = self.get_object()
        movement.status = 'cancelled'
        movement.save()
        messages.success(self.request, 'Movement cancelled successfully!')
        return redirect('movements:detail', pk=movement.pk)


class StartStockTakeView(LoginRequiredMixin, UpdateView):
    model = StockTake
    template_name = 'movements/stock_take_start.html'
    fields = []
    
    def form_valid(self, form):
        stock_take = self.get_object()
        stock_take.status = 'in_progress'
        stock_take.save()
        messages.success(self.request, 'Stock take started successfully!')
        return redirect('movements:stock_take_detail', pk=stock_take.pk)


class CompleteStockTakeView(LoginRequiredMixin, UpdateView):
    model = StockTake
    template_name = 'movements/stock_take_complete.html'
    fields = []
    
    def form_valid(self, form):
        stock_take = self.get_object()
        stock_take.status = 'completed'
        stock_take.save()
        messages.success(self.request, 'Stock take completed successfully!')
        return redirect('movements:stock_take_detail', pk=stock_take.pk)


class TrackMovementAPIView(LoginRequiredMixin, DetailView):
    model = Movement
    
    def get_object(self, queryset=None):
        tracking_number = self.kwargs.get('tracking_number')
        return get_object_or_404(Movement, tracking_number=tracking_number)
    
    def get(self, request, *args, **kwargs):
        movement = self.get_object()
        data = {
            'tracking_number': movement.tracking_number,
            'status': movement.status,
            'asset': movement.asset.asset_id,
            'from_location': movement.from_location.name,
            'to_location': movement.to_location.name,
            'created_at': movement.created_at.isoformat(),
            'expected_arrival': movement.expected_arrival_date.isoformat() if movement.expected_arrival_date else None,
        }
        return JsonResponse(data)
