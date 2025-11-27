from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from assets.models import Asset
from movements.models import Movement, BulkMovement, StockTake
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
from accounts.models import User, ActivityLog


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
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        export_type = request.GET.get('type', 'assets')
        export_format = request.GET.get('format', 'csv')
        
        if export_type == 'assets':
            if export_format == 'pdf':
                return self.export_assets_pdf(request)
            return self.export_assets(request)
        elif export_type == 'movements':
            if export_format == 'pdf':
                return self.export_movements_pdf(request)
            return self.export_movements(request)
        elif export_type == 'stock_takes':
            if export_format == 'pdf':
                return self.export_stock_takes_pdf(request)
            return self.export_stock_takes(request)
        
        return JsonResponse({'status': 'error', 'message': 'Invalid export type'})
    
    def export_assets(self, request):
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="assets_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Asset ID', 'Name', 'Category', 'Description', 'Serial Number', 
                        'Purchase Date', 'Purchase Price', 'Current Location', 'Status', 
                        'Condition', 'Warranty Expiry', 'Created At'])
        
        assets = Asset.objects.select_related('category', 'current_location').order_by('asset_id')
        
        for asset in assets:
            writer.writerow([
                asset.asset_id,
                asset.name,
                asset.category.name if asset.category else '',
                asset.description or '',
                asset.serial_number or '',
                asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else '',
                asset.purchase_price or '',
                asset.current_location.name if asset.current_location else '',
                asset.get_status_display(),
                asset.get_condition_display(),
                asset.warranty_expiry.strftime('%Y-%m-%d') if asset.warranty_expiry else '',
                asset.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    def export_movements(self, request):
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="movements_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Tracking Number', 'Asset ID', 'Asset Name', 'From Location', 
                        'To Location', 'Status', 'Priority', 'Reason', 'Initiated By', 
                        'Expected Arrival', 'Actual Arrival', 'Created At'])
        
        movements = Movement.objects.select_related('asset', 'from_location', 'to_location', 'initiated_by').order_by('-created_at')
        
        for movement in movements:
            writer.writerow([
                movement.tracking_number,
                movement.asset.asset_id,
                movement.asset.name,
                movement.from_location.name,
                movement.to_location.name,
                movement.get_status_display(),
                movement.get_priority_display(),
                movement.reason,
                movement.initiated_by.username,
                movement.expected_arrival_date.strftime('%Y-%m-%d %H:%M:%S') if movement.expected_arrival_date else '',
                movement.actual_arrival_date.strftime('%Y-%m-%d %H:%M:%S') if movement.actual_arrival_date else '',
                movement.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    def export_stock_takes(self, request):
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="stock_takes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Stock Take ID', 'Location', 'Status', 'Conducted By', 
                        'Scheduled Date', 'Completed Date', 'Notes', 'Created At'])
        
        stock_takes = StockTake.objects.select_related('location', 'conducted_by').order_by('-created_at')
        
        for stock_take in stock_takes:
            writer.writerow([
                stock_take.stock_take_id,
                stock_take.location.name,
                stock_take.get_status_display(),
                stock_take.conducted_by.username,
                stock_take.scheduled_date.strftime('%Y-%m-%d %H:%M:%S') if stock_take.scheduled_date else '',
                stock_take.completed_date.strftime('%Y-%m-%d %H:%M:%S') if stock_take.completed_date else '',
                stock_take.notes or '',
                stock_take.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    def export_assets_pdf(self, request):
        from django.http import HttpResponse
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from datetime import datetime
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="assets_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>Assets Export Report</b><br/><font size=10>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Data
        data = [['Asset ID', 'Name', 'Category', 'Location', 'Status', 'Condition', 'Purchase Date']]
        
        assets = Asset.objects.select_related('category', 'current_location').order_by('asset_id')
        
        for asset in assets:
            data.append([
                asset.asset_id,
                asset.name[:30] if len(asset.name) > 30 else asset.name,
                asset.category.name if asset.category else '',
                asset.current_location.name[:20] if asset.current_location else '',
                asset.get_status_display(),
                asset.get_condition_display(),
                asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else ''
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        return response
    
    def export_movements_pdf(self, request):
        from django.http import HttpResponse
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_LEFT
        from datetime import datetime
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="movements_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=landscape(A4), topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>Asset Movements Export Report</b><br/><font size=10>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Get bulk movements
        bulk_movements = BulkMovement.objects.select_related('from_location', 'to_location', 'initiated_by').prefetch_related('assets__category').order_by('-created_at')
        
        # Process each bulk movement
        for idx, bulk_movement in enumerate(bulk_movements):
            if idx > 0:
                elements.append(PageBreak())
            
            # Bulk Movement Header
            header_style = ParagraphStyle('header', parent=styles['Heading2'], textColor=colors.HexColor('#1f497d'))
            header = Paragraph(f"<b>Bulk Movement: {bulk_movement.tracking_number}</b>", header_style)
            elements.append(header)
            elements.append(Spacer(1, 0.1*inch))
            
            # Movement details
            detail_style = ParagraphStyle('detail', parent=styles['Normal'], fontSize=9, wordWrap='CJK')
            detail_data = [
                ['Description:', Paragraph(bulk_movement.reason or '', detail_style)],
                ['From Location:', Paragraph(bulk_movement.from_location.name, detail_style)],
                ['To Location:', Paragraph(bulk_movement.to_location.name, detail_style)],
                ['Status:', bulk_movement.get_status_display()],
                ['Priority:', bulk_movement.get_priority_display()],
                ['Expected Arrival:', bulk_movement.expected_arrival_date.strftime('%Y-%m-%d %H:%M') if bulk_movement.expected_arrival_date else ''],
                ['Initiated By:', bulk_movement.initiated_by.username],
                ['Total Assets:', str(bulk_movement.asset_count)],
            ]
            
            if bulk_movement.notes:
                detail_data.append(['Notes:', Paragraph(bulk_movement.notes, detail_style)])
            
            detail_table = Table(detail_data, colWidths=[2*inch, 8*inch])
            detail_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(detail_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Assets list header
            assets_header = Paragraph("<b>Assets in This Movement:</b>", styles['Heading3'])
            elements.append(assets_header)
            elements.append(Spacer(1, 0.1*inch))
            
            # Assets table
            asset_data = [['#', 'Asset ID', 'Asset Name', 'Category', 'Serial Number', 'Description']]

            # Style for description text wrapping
            desc_style = ParagraphStyle('desc', parent=styles['Normal'], fontSize=8, wordWrap='CJK')

            assets = bulk_movement.assets.select_related('category').order_by('asset_id')
            for i, asset in enumerate(assets, 1):
                asset_data.append([
                    str(i),
                    asset.asset_id,
                    asset.name,
                    asset.category.name if asset.category else '',
                    asset.serial_number or '',
                    Paragraph(asset.description or '', desc_style)
                ])

            asset_table = Table(asset_data, colWidths=[0.3*inch, 1*inch, 1.5*inch, 0.9*inch, 1*inch, 3.8*inch])
            asset_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f497d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            elements.append(asset_table)
        
        # Add single movements if any
        single_movements = Movement.objects.select_related('asset', 'from_location', 'to_location', 'initiated_by').order_by('-created_at')
        
        if single_movements.exists():
            if bulk_movements.exists():
                elements.append(PageBreak())
            
            single_header = Paragraph("<b>Single Asset Movements</b>", styles['Heading2'])
            elements.append(single_header)
            elements.append(Spacer(1, 0.2*inch))
            
            single_data = [['Tracking #', 'Asset', 'From', 'To', 'Reason', 'Status', 'Date']]
            
            for movement in single_movements:
                single_data.append([
                    movement.tracking_number,
                    f"{movement.asset.asset_id}\n{movement.asset.name}",
                    movement.from_location.name,
                    movement.to_location.name,
                    movement.reason,
                    movement.get_status_display(),
                    movement.expected_arrival_date.strftime('%Y-%m-%d') if movement.expected_arrival_date else ''
                ])
            
            single_table = Table(single_data, colWidths=[1.2*inch, 1.5*inch, 1.8*inch, 1.8*inch, 1.5*inch, 0.8*inch, 0.8*inch])
            single_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            elements.append(single_table)
        
        doc.build(elements)
        return response
    
    def export_stock_takes_pdf(self, request):
        from django.http import HttpResponse
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from datetime import datetime
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="stock_takes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>Stock Takes Export Report</b><br/><font size=10>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Data
        data = [['Stock Take ID', 'Location', 'Status', 'Conducted By', 'Scheduled Date', 'Created At']]
        
        stock_takes = StockTake.objects.select_related('location', 'conducted_by').order_by('-created_at')
        
        for stock_take in stock_takes:
            data.append([
                stock_take.stock_take_id,
                stock_take.location.name[:25] if len(stock_take.location.name) > 25 else stock_take.location.name,
                stock_take.get_status_display(),
                stock_take.conducted_by.username,
                stock_take.scheduled_date.strftime('%Y-%m-%d') if stock_take.scheduled_date else '',
                stock_take.created_at.strftime('%Y-%m-%d')
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        return response


class DashboardStatsAPIView(LoginRequiredMixin, View):
    def get(self, request):
        return JsonResponse({'message': 'API endpoint ready'})


class ActivityLogView(LoginRequiredMixin, ListView):
    """View to display user activity logs"""
    model = ActivityLog
    template_name = 'dashboard/activity_log.html'
    context_object_name = 'activities'
    paginate_by = 50

    def get_queryset(self):
        queryset = ActivityLog.objects.select_related('user').order_by('-created_at')

        # Filter by user
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by action type
        action_type = self.request.GET.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)

        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(is_active=True).order_by('username')
        context['action_types'] = ActivityLog.ACTION_TYPES
        return context
