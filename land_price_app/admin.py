# Import Django admin module
from django.contrib import admin
# Import our database models
from .models import LandPrediction, ContactMessage, BlogPost

# Register LandPrediction model with admin panel
# This decorator tells Django to show this model in admin
@admin.register(LandPrediction)
class LandPredictionAdmin(admin.ModelAdmin):
    # Which fields to show in the list view (table of all predictions)
    list_display = ('village', 'area_sqft', 'predicted_price', 'user', 'created_at')
    
    # Add filter sidebar on right side (filter by these fields)
    list_filter = ('village', 'land_use', 'soil_type', 'created_at')
    
    # Add search box (search in these fields)
    search_fields = ('village', 'user__username')  # user__username means search in user's username
    
    # Default sorting (newest first)
    ordering = ('-created_at',)
    
    # Fields that cannot be edited (read-only)
    readonly_fields = ('predicted_price', 'created_at')
    
    # Group fields into sections in the edit form
    fieldsets = (
        # Section 1: Location Details
        ('Location Details', {
            'fields': ('village', 'distance_to_city_km')
        }),
        # Section 2: Land Details
        ('Land Details', {
            'fields': ('area_sqft', 'land_use', 'soil_type')
        }),
        # Section 3: Amenities
        ('Amenities', {
            'fields': ('road_access', 'water_source', 'electricity_available')
        }),
        # Section 4: Development
        ('Development', {
            'fields': ('nearby_development',)
        }),
        # Section 5: Prediction Results
        ('Prediction', {
            'fields': ('predicted_price', 'created_at')
        }),
        # Section 6: User Information
        ('User Information', {
            'fields': ('user',)
        }),
    )

# Register ContactMessage model with admin panel
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # Show these fields in list view
    list_display = ('name', 'email', 'created_at')
    
    # Filter by creation date
    list_filter = ('created_at',)
    
    # Search in name, email, and message content
    search_fields = ('name', 'email', 'message')
    
    # Cannot edit creation date
    readonly_fields = ('created_at',)
    
    # Sort by newest first
    ordering = ('-created_at',)

# Register BlogPost model with admin panel
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    # Show these fields in list view
    list_display = ('title', 'author', 'category', 'featured', 'views', 'created_at')
    
    # Filter by category, featured status, and date
    list_filter = ('category', 'featured', 'created_at')
    
    # Search in title, summary, content, and author
    search_fields = ('title', 'summary', 'content', 'author')
    
    # Automatically create slug from title (URL-friendly version)
    # When you type title, slug is auto-generated
    prepopulated_fields = {'slug': ('title',)}
    
    # These fields cannot be edited manually
    readonly_fields = ('views', 'created_at', 'updated_at')
    
    # Sort by newest first
    ordering = ('-created_at',)
    
    # Group fields into sections
    fieldsets = (
        # Section 1: Basic Information
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'featured')
        }),
        # Section 2: Content
        ('Content', {
            'fields': ('image', 'summary', 'content')
        }),
        # Section 3: Statistics (read-only)
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at')
        }),
    )
