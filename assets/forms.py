from django import forms
from .models import Asset, AssetCategory


class DateInput(forms.DateInput):
    """Custom date input widget with HTML5 date picker"""
    input_type = 'date'


class AssetForm(forms.ModelForm):
    """Form for creating and updating assets with user-friendly date pickers"""
    
    # Make description optional in the form
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter detailed description (optional)'
        }),
        required=False
    )
    
    # Make condition and status optional with defaults
    condition = forms.ChoiceField(
        choices=Asset.CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        initial='good'
    )
    
    status = forms.ChoiceField(
        choices=Asset.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        initial='available'
    )
    
    class Meta:
        model = Asset
        fields = [
            'asset_id', 'name', 'description', 'category',
            'serial_number', 'model_number', 'manufacturer',
            'purchase_date', 'purchase_value', 'current_value',
            'warranty_expiry', 'current_location', 'primary_user', 'responsible_person',
            'condition', 'status', 'notes'
        ]
        widgets = {
            'asset_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter asset ID (e.g., ASSET-001)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter asset name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter serial number (optional)'
            }),
            'model_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter model number (optional)'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter manufacturer name (optional)'
            }),
            'purchase_date': DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD'
            }),
            'warranty_expiry': DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD'
            }),
            'purchase_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'current_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'current_location': forms.Select(attrs={
                'class': 'form-select'
            }),
            'primary_user': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsible_person': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional notes or comments (optional)'
            }),
        }
        labels = {
            'asset_id': 'Asset ID',
            'purchase_date': 'Purchase Date',
            'purchase_value': 'Purchase Value ($)',
            'current_value': 'Current Value ($)',
            'warranty_expiry': 'Warranty Expiry Date',
            'current_location': 'Current Location',
            'primary_user': 'Primary User',
            'responsible_person': 'Responsible Person',
        }
        help_texts = {
            'purchase_date': 'Use the date picker or enter in YYYY-MM-DD format',
            'warranty_expiry': 'Use the date picker or enter in YYYY-MM-DD format',
            'purchase_value': 'Original purchase price',
            'current_value': 'Current estimated value',
            'description': 'Optional detailed description of the asset',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make current_location and responsible_person show empty option
        self.fields['current_location'].empty_label = "Select location"
        self.fields['primary_user'].empty_label = "Select primary user (optional)"
        self.fields['primary_user'].required = False
        self.fields['responsible_person'].empty_label = "Select person (optional)"
        self.fields['responsible_person'].required = False
    
    def clean_description(self):
        """Ensure description is never completely empty"""
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            return ''  # Return empty string instead of None
        return description
    
    def clean_condition(self):
        """Provide default value for condition if not specified"""
        condition = self.cleaned_data.get('condition')
        if not condition:
            return 'good'
        return condition
    
    def clean_status(self):
        """Provide default value for status if not specified"""
        status = self.cleaned_data.get('status')
        if not status:
            return 'available'
        return status


class AssetUpdateForm(AssetForm):
    """Form for updating existing assets (excludes asset_id)"""

    class Meta(AssetForm.Meta):
        fields = [
            'name', 'description', 'category',
            'serial_number', 'model_number', 'manufacturer',
            'purchase_date', 'purchase_value', 'current_value',
            'warranty_expiry', 'current_location', 'primary_user', 'responsible_person',
            'condition', 'status', 'notes'
        ]


class AssetCategoryForm(forms.ModelForm):
    """Form for creating and updating asset categories"""
    
    class Meta:
        model = AssetCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Category description (optional)'
            }),
        }
