from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q

from .models import Movement, StockTake, MovementAcknowledgement, BulkMovement
from assets.models import Asset
from accounts.models import ActivityLog


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


class BulkMovementCreateView(LoginRequiredMixin, TemplateView):
    """Create multiple movement records in one transaction"""
    template_name = 'movements/bulk_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from locations.models import Location
        context['locations'] = Location.objects.all().order_by('name')
        context['assets'] = Asset.objects.select_related(
            'category', 'current_location'
        ).order_by('asset_id')

        # Add reminder for users
        messages.info(
            self.request,
            '<strong>Reminder:</strong> After creating this movement, it will be in <span class="badge bg-warning">Pending</span> status. '
            'A different user (Movement Approver or Administrator) must approve and complete the movement. '
            '<strong>You cannot approve your own movement request.</strong>',
            extra_tags='safe'
        )
        return context
    
    def post(self, request, *args, **kwargs):
        from django.db import transaction
        from datetime import datetime
        
        # Get form data
        asset_ids = request.POST.getlist('assets')
        from_location_id = request.POST.get('from_location')
        to_location_id = request.POST.get('to_location')
        reason = request.POST.get('reason')
        notes = request.POST.get('notes', '')
        expected_arrival = request.POST.get('expected_arrival_date')
        priority = request.POST.get('priority', 'normal')
        
        # Validate
        if not asset_ids:
            messages.error(request, 'Please select at least one asset to move.')
            return redirect('movements:bulk_create')
        
        if from_location_id == to_location_id:
            messages.error(request, 'From Location and To Location must be different.')
            return redirect('movements:bulk_create')
        
        # Create single bulk movement with multiple assets
        try:
            with transaction.atomic():
                from locations.models import Location
                from_location = Location.objects.get(id=from_location_id)
                to_location = Location.objects.get(id=to_location_id)
                
                # Create the bulk movement record
                bulk_movement = BulkMovement.objects.create(
                    from_location=from_location,
                    to_location=to_location,
                    reason=reason,
                    notes=notes,
                    expected_arrival_date=expected_arrival,
                    priority=priority,
                    initiated_by=request.user,
                    status='pending'
                )
                
                # Add all selected assets to the bulk movement
                assets = Asset.objects.filter(id__in=asset_ids)
                bulk_movement.assets.set(assets)
                
                # Log the activity
                ActivityLog.log(
                    user=request.user,
                    action_type='bulk_movement_create',
                    description=f'Created bulk movement {bulk_movement.tracking_number} with {len(asset_ids)} asset(s) from {from_location.name} to {to_location.name}',
                    request=request,
                    target_model='BulkMovement',
                    target_id=bulk_movement.tracking_number
                )

                messages.success(
                    request,
                    f'Successfully created bulk movement {bulk_movement.tracking_number} with {len(asset_ids)} asset(s)!'
                )
                return redirect('movements:bulk_detail', pk=bulk_movement.pk)
                
        except Exception as e:
            messages.error(request, f'Error creating movements: {str(e)}')
            return redirect('movements:bulk_create')


class BulkMovementListView(LoginRequiredMixin, ListView):
    """List all bulk movements"""
    model = BulkMovement
    template_name = 'movements/bulk_list.html'
    context_object_name = 'bulk_movements'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = BulkMovement.objects.select_related(
            'from_location', 'to_location', 'initiated_by'
        ).prefetch_related('assets').order_by('-created_at')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = BulkMovement.STATUS_CHOICES
        return context


class BulkMovementDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single bulk movement"""
    model = BulkMovement
    template_name = 'movements/bulk_detail.html'
    context_object_name = 'bulk_movement'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assets'] = self.object.assets.select_related('category', 'current_location').order_by('asset_id')
        return context


class BulkMovementUpdateView(LoginRequiredMixin, UpdateView):
    """Update bulk movement status and details"""
    model = BulkMovement
    template_name = 'movements/bulk_form.html'
    fields = ['status', 'reason', 'notes', 'expected_arrival_date', 'priority']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bulk_movement = self.get_object()

        # Check if current user is the initiator
        is_initiator = self.request.user == bulk_movement.initiated_by
        context['is_initiator'] = is_initiator
        context['can_approve'] = not is_initiator or self.request.user.is_superuser

        if is_initiator and not self.request.user.is_superuser:
            messages.warning(
                self.request,
                '<strong>Restriction:</strong> You cannot approve this movement because you created it. '
                'A different user (Movement Approver or Administrator) must change the status to Completed or Delivered.',
                extra_tags='safe'
            )
        return context

    def form_valid(self, form):
        bulk_movement = self.get_object()
        new_status = form.cleaned_data.get('status')
        old_status = bulk_movement.status

        # Check if user is trying to approve their own movement
        is_initiator = self.request.user == bulk_movement.initiated_by
        is_approving = new_status in ['completed', 'delivered', 'in_transit'] and old_status == 'pending'

        if is_initiator and is_approving and not self.request.user.is_superuser:
            messages.error(
                self.request,
                'You cannot approve your own movement request. A different user must approve this movement.'
            )
            return redirect('movements:bulk_detail', pk=bulk_movement.pk)

        # Record who approved the movement and log the activity
        if new_status in ['completed', 'delivered'] and old_status != new_status:
            form.instance.approved_by = self.request.user
            ActivityLog.log(
                user=self.request.user,
                action_type='bulk_movement_approve',
                description=f'Approved bulk movement {bulk_movement.tracking_number} - Status changed from {old_status} to {new_status}',
                request=self.request,
                target_model='BulkMovement',
                target_id=bulk_movement.tracking_number
            )
        elif new_status != old_status:
            ActivityLog.log(
                user=self.request.user,
                action_type='bulk_movement_update',
                description=f'Updated bulk movement {bulk_movement.tracking_number} - Status changed from {old_status} to {new_status}',
                request=self.request,
                target_model='BulkMovement',
                target_id=bulk_movement.tracking_number
            )

        messages.success(self.request, 'Bulk movement updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('movements:bulk_detail', kwargs={'pk': self.object.pk})
