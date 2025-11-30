# Import Django's database models to create database tables
from django.db import models
# Import settings to access user model
from django.conf import settings

# This class creates a database table to store land price predictions
# Each prediction will be saved as a row in this table
class LandPrediction(models.Model):
    # Link to user who made the prediction (optional - can be None)
    # If user is deleted, set this field to None instead of deleting prediction
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Village name where the land is located (text field, max 150 characters)
    village = models.CharField(max_length=150)
    
    # Area of land in square feet (decimal number)
    area_sqft = models.FloatField()
    
    # Distance from city center in kilometers (decimal number)
    distance_to_city_km = models.FloatField()
    
    # Type of road access (e.g., "Highway", "City Road", "Rural Road")
    road_access = models.CharField(max_length=100)
    
    # Water source available (e.g., "Well", "Borewell", "River")
    water_source = models.CharField(max_length=100)
    
    # Whether electricity is available (True or False)
    electricity_available = models.BooleanField()
    
    # How the land will be used (e.g., "Agricultural", "Residential", "Commercial")
    land_use = models.CharField(max_length=100)
    
    # Type of soil (e.g., "Clay", "Sandy", "Loamy", "Rocky")
    soil_type = models.CharField(max_length=100)
    
    # Level of nearby development (e.g., "Low", "Medium", "High")
    nearby_development = models.CharField(max_length=200)
    
    # The predicted price per square foot (calculated by ML model)
    predicted_price = models.FloatField()
    
    # Automatically saves the date and time when prediction is created
    created_at = models.DateTimeField(auto_now_add=True)

    # This function defines how the object is displayed in admin panel
    # Example: "Pune - ₹5000/sqft (2025-01-15)"
    def __str__(self):
        return f"{self.village} - ₹{self.predicted_price}/sqft ({self.created_at.date()})"

    # Meta class contains extra information about the model
    class Meta:
        # Order predictions by newest first (minus sign means descending order)
        ordering = ['-created_at']

# This class creates a table to store messages from contact form
class ContactMessage(models.Model):
    # Name of the person sending the message (text, max 120 characters)
    name = models.CharField(max_length=120)
    
    # Email address (validates that it's a proper email format)
    email = models.EmailField()
    
    # The actual message content (can be long text)
    message = models.TextField()
    
    # Automatically saves when the message was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Display format in admin: "John Doe <john@example.com>"
    def __str__(self):
        return f"{self.name} <{self.email}>"

# This class creates a table to store blog posts/articles
class BlogPost(models.Model):
    # Define categories that blog posts can belong to
    # Format: (value_in_database, display_name)
    CATEGORY_CHOICES = [
        ('technology', 'Technology'),        # Tech-related posts
        ('market', 'Market Analysis'),        # Market analysis posts
        ('tips', 'Buying Tips'),             # Tips for buyers
        ('legal', 'Legal Guide'),            # Legal information
        ('investment', 'Investment'),        # Investment advice
        ('general', 'General'),              # General topics
    ]
    
    # Title of the blog post (text, max 200 characters)
    title = models.CharField(max_length=200)
    
    # URL-friendly version of title (e.g., "how-to-buy-land" from "How to Buy Land")
    # Must be unique - no two posts can have same slug
    slug = models.SlugField(max_length=200, unique=True)
    
    # Author name (defaults to 'Admin' if not specified)
    author = models.CharField(max_length=100, default='Admin')
    
    # Category from the choices above (defaults to 'general')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    
    # URL to the blog post image (optional - can be blank)
    image = models.URLField(max_length=500, blank=True, help_text='URL to blog post image')
    
    # Short summary shown in blog listing (max 300 characters)
    summary = models.TextField(max_length=300, help_text='Short summary for blog listing')
    
    # Full blog post content (can be very long)
    content = models.TextField(help_text='Full blog post content')
    
    # Whether this post should be featured on homepage (True/False)
    featured = models.BooleanField(default=False, help_text='Show on homepage')
    
    # Number of times this post has been viewed (starts at 0)
    views = models.IntegerField(default=0)
    
    # When the post was first created (auto-saved)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # When the post was last updated (auto-updated every time post is saved)
    updated_at = models.DateTimeField(auto_now=True)

    # Meta class with extra settings
    class Meta:
        # Show newest posts first
        ordering = ['-created_at']
        # How to display in admin panel (singular)
        verbose_name = 'Blog Post'
        # How to display in admin panel (plural)
        verbose_name_plural = 'Blog Posts'

    # Display the title in admin panel
    def __str__(self):
        return self.title
    
    # Generate the URL for this blog post
    # Example: /blog/how-to-buy-land/
    def get_absolute_url(self):
        from django.urls import reverse
        # Create URL using the slug
        return reverse('land_price_app:blog_detail', kwargs={'slug': self.slug})