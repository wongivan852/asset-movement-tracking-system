from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from assets.models import Asset
from movements.models import Movement
from locations.models import Location

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.views import View
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from assets.models import Asset, AssetCategory
from locations.models import Location
from movements.models import Movement, StockTake
from accounts.models import User


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic statistics
        context['total_assets'] = Asset.objects.count()
        context['total_locations'] = Location.objects.filter(is_active=True).count()
        context['total_users'] = User.objects.filter(is_active=True).count()
        
        # Asset statistics by status
        context['assets_available'] = Asset.objects.filter(status='available').count()
        context['assets_in_transit'] = Asset.objects.filter(status='in_transit').count()
        context['assets_in_use'] = Asset.objects.filter(status='in_use').count()
        context['assets_maintenance'] = Asset.objects.filter(status='maintenance').count()
        
        # Recent movements
        context['recent_movements'] = Movement.objects.select_related(
            'asset', 'from_location', 'to_location', 'initiated_by'
        ).order_by('-created_at')[:10]
        
        # Overdue movements
        context['overdue_movements'] = Movement.objects.select_related(
            'asset', 'from_location', 'to_location'
        ).filter(
            expected_arrival_date__lt=timezone.now(),
            status__in=['pending', 'in_transit']
        ).count()
        
        # Pending acknowledgements
        context['pending_acknowledgements'] = Movement.objects.filter(
            status='delivered'
        ).count()
        
        # Recent stock takes
        context['recent_stock_takes'] = StockTake.objects.select_related(
            'location', 'conducted_by'
        ).order_by('-created_at')[:5]
        
        return context


class DashboardStatsAPIView(LoginRequiredMixin, View):
    def get(self, request):
        # Asset status distribution
        asset_stats = Asset.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Assets by location
        location_stats = Asset.objects.values(
            'current_location__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Monthly movement trends (last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_movements = Movement.objects.filter(
            created_at__gte=six_months_ago
        ).extra(
            select={'month': "strftime('%%Y-%%m', created_at)"}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return JsonResponse({
            'asset_stats': list(asset_stats),
            'location_stats': list(location_stats),
            'monthly_movements': list(monthly_movements),
        })


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        notifications = []
        
        # Overdue movements
        overdue_movements = Movement.objects.select_related(
            'asset', 'from_location', 'to_location'
        ).filter(
            expected_arrival_date__lt=timezone.now(),
            status__in=['pending', 'in_transit']
        )
        
        for movement in overdue_movements:
            notifications.append({
                'type': 'overdue_movement',
                'title': f'Overdue Movement: {movement.tracking_number}',
                'message': f'Asset {movement.asset.asset_id} movement from {movement.from_location} to {movement.to_location} is overdue.',
                'created_at': movement.expected_arrival_date,
                'priority': 'high',
                'url': f'/movements/{movement.id}/'
            })
        
        # Pending acknowledgements
        pending_acks = Movement.objects.select_related(
            'asset', 'to_location'
        ).filter(status='delivered')
        
        for movement in pending_acks:
            notifications.append({
                'type': 'pending_acknowledgement',
                'title': f'Pending Acknowledgement: {movement.tracking_number}',
                'message': f'Asset {movement.asset.asset_id} delivered to {movement.to_location} needs acknowledgement.',
                'created_at': movement.actual_arrival_date or movement.expected_arrival_date,
                'priority': 'medium',
                'url': f'/movements/{movement.id}/acknowledge/'
            })
        
        # Sort by priority and date
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        notifications.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['created_at']))
        
        return notifications


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Asset summary by category
        context['assets_by_category'] = AssetCategory.objects.annotate(
            asset_count=Count('assets')
        ).order_by('-asset_count')
        
        # Assets by location
        context['assets_by_location'] = Location.objects.annotate(
            asset_count=Count('assets')
        ).order_by('-asset_count')
        
        # Movement statistics
        context['movement_stats'] = {
            'total_movements': Movement.objects.count(),
            'completed_movements': Movement.objects.filter(status='acknowledged').count(),
            'pending_movements': Movement.objects.filter(status='pending').count(),
            'in_transit_movements': Movement.objects.filter(status='in_transit').count(),
            'cancelled_movements': Movement.objects.filter(status='cancelled').count(),
        }
        
        return context


class ExportDataView(LoginRequiredMixin, View):
    def get(self, request):
        export_type = request.GET.get('type', 'assets')
        
        if export_type == 'assets':
            # Asset export logic would go here
            pass
        elif export_type == 'movements':
            # Movement export logic would go here
            pass
        elif export_type == 'stock_takes':
            # Stock take export logic would go here
            pass
        
        return JsonResponse({'status': 'success', 'message': 'Export functionality to be implemented'})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic statistics
        context.update({
            'total_assets': Asset.objects.count(),
            'assets_in_transit': Asset.objects.filter(status='in_transit').count(),
            'total_locations': Location.objects.filter(is_active=True).count(),
            'pending_movements': Movement.objects.filter(status='pending').count(),
            'overdue_movements': Movement.objects.filter(
                status='in_transit',
                expected_arrival_date__lt=timezone.now()
            ).count(),
        })
        return context

class DashboardStatsAPIView(LoginRequiredMixin, View):
    def get(self, request):
        return JsonResponse({'message': 'API endpoint ready'})

class NotificationListView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/notifications.html'

class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/reports.html'

class ExportDataView(LoginRequiredMixin, View):
    def get(self, request):
        return JsonResponse({'message': 'Export functionality coming soon'})
