from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q

from .models import Asset, AssetCategory, AssetRemark
from locations.models import Location


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/list.html'
    context_object_name = 'assets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Asset.objects.select_related(
            'category', 'current_location', 'responsible_person'
        ).order_by('asset_id')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(asset_id__icontains=search) |
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(current_location_id=location)
            
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = AssetCategory.objects.filter(is_active=True)
        context['locations'] = Location.objects.filter(is_active=True)
        context['statuses'] = Asset.STATUS_CHOICES
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'assets/detail.html'
    context_object_name = 'asset'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_movements'] = self.object.movements.select_related(
            'from_location', 'to_location', 'initiated_by'
        ).order_by('-created_at')[:10]
        context['remarks'] = self.object.remarks.select_related(
            'created_by'
        ).order_by('-created_at')[:10]
        return context


class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    template_name = 'assets/form.html'
    fields = ['asset_id', 'name', 'description', 'category', 'serial_number', 
              'model_number', 'manufacturer', 'purchase_date', 'purchase_value', 
              'current_value', 'current_location', 'responsible_person', 'condition']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Asset {form.instance.asset_id} created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('assets:detail', kwargs={'pk': self.object.pk})


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    template_name = 'assets/form.html'
    fields = ['name', 'description', 'category', 'serial_number', 'model_number', 
              'manufacturer', 'purchase_date', 'purchase_value', 'current_value', 
              'current_location', 'responsible_person', 'condition', 'status', 'notes']
    
    def form_valid(self, form):
        messages.success(self.request, f'Asset {form.instance.asset_id} updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('assets:detail', kwargs={'pk': self.object.pk})


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    model = Asset
    template_name = 'assets/delete.html'
    success_url = reverse_lazy('assets:list')
    
    def delete(self, request, *args, **kwargs):
        asset = self.get_object()
        messages.success(request, f'Asset {asset.asset_id} deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CategoryListView(LoginRequiredMixin, ListView):
    model = AssetCategory
    template_name = 'assets/categories.html'
    context_object_name = 'categories'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = AssetCategory
    template_name = 'assets/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('assets:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Category {form.instance.name} created successfully!')
        return super().form_valid(form)


class AssetRemarksView(LoginRequiredMixin, ListView):
    model = AssetRemark
    template_name = 'assets/remarks.html'
    context_object_name = 'remarks'
    paginate_by = 20
    
    def get_queryset(self):
        self.asset = get_object_or_404(Asset, pk=self.kwargs['asset_id'])
        return AssetRemark.objects.filter(asset=self.asset).select_related(
            'created_by'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset'] = self.asset
        return context


class AddRemarkView(LoginRequiredMixin, CreateView):
    model = AssetRemark
    template_name = 'assets/add_remark.html'
    fields = ['category', 'remark', 'is_important']
    
    def form_valid(self, form):
        self.asset = get_object_or_404(Asset, pk=self.kwargs['asset_id'])
        form.instance.asset = self.asset
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Remark added successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset'] = get_object_or_404(Asset, pk=self.kwargs['asset_id'])
        return context
    
    def get_success_url(self):
        return reverse_lazy('assets:remarks', kwargs={'asset_id': self.kwargs['asset_id']})


class AssetSearchView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/search.html'
    context_object_name = 'assets'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Asset.objects.filter(
                Q(asset_id__icontains=query) |
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(serial_number__icontains=query)
            ).select_related('category', 'current_location')
        return Asset.objects.none()
