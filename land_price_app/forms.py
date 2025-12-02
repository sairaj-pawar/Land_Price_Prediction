# Import Django form classes
from django import forms  # Base form classes
from django.contrib.auth.forms import UserCreationForm  # Built-in user registration form
from django.contrib.auth.models import User  # User model
from .models import LandPrediction  # Our prediction model

# This form collects land details from user for price prediction
class LandPredictionForm(forms.ModelForm):
    # Define choices for road access dropdown
    ROAD_ACCESS_CHOICES = [
        ('Rural Road', 'Rural Road'),    # Option 1: Rural Road
        ('City Road', 'City Road'),      # Option 2: City Road
        ('Highway', 'Highway'),          # Option 3: Highway
    ]
    
    # Define choices for water source dropdown
    WATER_SOURCE_CHOICES = [
        ('Well', 'Well'),                # Option 1: Well
        ('Borewell', 'Borewell'),        # Option 2: Borewell
        ('River', 'River'),              # Option 3: River
        ('None', 'None'),                # Option 4: No water source
    ]
    
    # Define choices for land use dropdown
    LAND_USE_CHOICES = [
        ('Agricultural', 'Agricultural'),    # For farming
        ('Commercial', 'Commercial'),        # For business
        ('Residential', 'Residential'),      # For housing
    ]
    
    # Define choices for soil type dropdown
    SOIL_TYPE_CHOICES = [
        ('Clay', 'Clay'),        # Clay soil
        ('Sandy', 'Sandy'),      # Sandy soil
        ('Loamy', 'Loamy'),      # Loamy soil (best for farming)
        ('Rocky', 'Rocky'),      # Rocky soil
    ]
    
    # Define choices for nearby development level
    DEVELOPMENT_CHOICES = [
        ('Low', 'Low'),          # Low development
        ('Medium', 'Medium'),    # Medium development
        ('High', 'High'),        # High development
    ]
    
    # Define form fields with their input types and styling
    # CharField = text input, Select widget = dropdown menu
    village = forms.CharField(widget=forms.Select(attrs={'class': 'form-select', 'title': 'Select village'}))
    
    # FloatField = decimal number input
    # NumberInput = number input box, step='0.01' allows decimals
    area_sqft = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g., 1200'}))
    
    # Distance in kilometers (decimal number)
    distance_to_city_km = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g., 5'}))
    
    # ChoiceField = dropdown with predefined options
    road_access = forms.ChoiceField(choices=ROAD_ACCESS_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'title': 'Road access type'}))
    
    # Water source dropdown
    water_source = forms.ChoiceField(choices=WATER_SOURCE_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'title': 'Primary water source'}))
    
    # BooleanField = checkbox (True/False)
    # required=False means user can leave it unchecked
    electricity_available = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    # Land use dropdown
    land_use = forms.ChoiceField(choices=LAND_USE_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'title': 'Intended land use'}))
    
    # Soil type dropdown
    soil_type = forms.ChoiceField(choices=SOIL_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'title': 'Soil type'}))
    
    # Development level dropdown
    nearby_development = forms.ChoiceField(choices=DEVELOPMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'title': 'Development level'}))

    # Meta class tells Django which model this form is for
    class Meta:
        model = LandPrediction  # Link to LandPrediction model
        # Exclude these fields from form (we'll set them automatically)
        exclude = ['user', 'predicted_price', 'created_at']
    
    # This function runs when form is created
    def __init__(self, *args, **kwargs):
        # Call parent class __init__ to set up basic form
        super().__init__(*args, **kwargs)
        
        # Load village list from Excel file for dropdown
        import pandas as pd  # For reading Excel file
        import os            # For file paths
        
        # Get path to Excel file with village data
        # Go up two folders from current file, then find Excel file
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  '0a73f94e-90e3-4ebd-9d94-15dc8066ad52.xlsx')
        
        # Try reading the Excel (dataset) file; if it's missing or unreadable,
        # fall back to an empty list so the form doesn't crash at runtime.
        villages = []
        try:
            if os.path.exists(dataset_path):
                df = pd.read_excel(dataset_path)
                if 'Village' in df.columns:
                    villages = sorted(df['Village'].dropna().unique())
        except Exception:
            # If anything goes wrong (file not found, read error, bad data),
            # keep villages empty. We avoid raising exceptions in form init so the
            # site doesn't return 500 on render.
            villages = []
        
        # Set village dropdown choices (if any) or a default placeholder
        # Format: [(value, display_name), ...]
        if villages:
            self.fields['village'].widget.choices = [(v, v) for v in villages]
        else:
            # Keep a simple placeholder if the dataset isn't available
            self.fields['village'].widget.choices = [('', 'Select village')]


# This form handles user registration (sign up)
class CustomUserCreationForm(UserCreationForm):
    # Add email field (not in default UserCreationForm)
    # required=True means user must provide email
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Email',           # Hint text in input box
        'autocomplete': 'email'           # Browser autocomplete hint
    }))
    
    # Meta class links form to User model
    class Meta:
        model = User  # Django's built-in User model
        # Fields to show in form (in this order)
        fields = ('username', 'email', 'password1', 'password2')
    
    # Customize form when it's created
    def __init__(self, *args, **kwargs):
        # Call parent class __init__
        super().__init__(*args, **kwargs)
        
        # Add placeholder text and autocomplete hints to each field
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    
    # Override save function to also save email
    def save(self, commit=True):
        # Get user object from parent save (but don't save yet)
        user = super().save(commit=False)
        
        # Set email from form data
        user.email = self.cleaned_data['email']
        
        # If commit=True, save to database
        if commit:
            user.save()
        
        # Return the user object
        return user
