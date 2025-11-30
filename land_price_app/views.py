# Import necessary Django functions and classes
from django.shortcuts import render, redirect  # render: show HTML pages, redirect: go to another page
from django.contrib.auth.decorators import login_required  # Require user to be logged in
from django.contrib.auth import logout  # Function to log out user
from django.contrib import messages  # Show success/error messages to user
from django.db.models import Avg, Min, Max, Count  # Database calculation functions
from .models import LandPrediction, ContactMessage, BlogPost  # Import our database models
from .forms import LandPredictionForm, CustomUserCreationForm  # Import our forms
from .ml_helpers import predict_price  # Import ML prediction function

# This function shows the home page with prediction form
def home(request):
    """Home page with prediction form."""
    # Create an empty form for user to fill
    form = LandPredictionForm()
    
    # Calculate statistics from all predictions in database
    # aggregate() performs calculations on multiple records
    stats = LandPrediction.objects.aggregate(
        avg_price=Avg('predicted_price'),      # Average of all predicted prices
        min_price=Min('predicted_price'),      # Minimum price found
        max_price=Max('predicted_price'),      # Maximum price found
        total_predictions=Count('id')          # Count total number of predictions
    )

    # Get the 5 most recent predictions (order by newest first, limit to 5)
    recent_predictions = LandPrediction.objects.order_by('-created_at')[:5]
    
    # Calculate total value for each recent prediction (price × area)
    for pred in recent_predictions:
        pred.total_value = pred.predicted_price * pred.area_sqft

    # Prepare data to send to HTML template
    context = {
        'form': form,                          # The prediction form
        'avg_price': stats['avg_price'],       # Average price
        'min_price': stats['min_price'],       # Minimum price
        'max_price': stats['max_price'],       # Maximum price
        'total_predictions': stats['total_predictions'],  # Total count
        'recent_predictions': recent_predictions,  # Recent predictions list
    }

    # Show the home.html page with the context data
    return render(request, 'land_price_app/home.html', context)

# This function handles when user submits prediction form
def result(request):
    """Handle prediction form submission and display results."""
    # Check if form was submitted (POST request)
    if request.method == 'POST':
        # Create form with submitted data
        form = LandPredictionForm(request.POST)
        
        # Check if all form fields are valid
        if form.is_valid():
            # Get cleaned (validated) data from form
            data = form.cleaned_data
            
            # Call ML function to predict price based on input data
            predicted_price = predict_price(data)
            
            # Save form data but don't commit to database yet
            # commit=False means "prepare the object but don't save"
            prediction = form.save(commit=False)
            
            # Add the predicted price to the prediction object
            prediction.predicted_price = predicted_price
            
            # Link to current user if logged in, otherwise None
            prediction.user = request.user if request.user.is_authenticated else None
            
            # Now save to database
            prediction.save()
            
            # Calculate total land value (price per sqft × total area)
            total_value = predicted_price * data['area_sqft']
            
            # Show result page with prediction details
            return render(request, 'land_price_app/result.html', {
                'prediction': prediction,      # The saved prediction object
                'total_value': total_value     # Total calculated value
            })
    
    # If form not submitted or invalid, go back to home page
    return redirect('land_price_app:home')

# This decorator means user must be logged in to see dashboard
@login_required
def dashboard(request):
    """Analytics dashboard showing predictions and statistics."""
    # Import needed modules
    from django.utils import timezone  # For current date/time
    from datetime import timedelta     # For date calculations
    import json                        # For JSON data
    
    # Calculate basic statistics from all predictions
    stats = LandPrediction.objects.aggregate(
        avg_price=Avg('predicted_price'),           # Average price
        min_price=Min('predicted_price'),           # Minimum price
        max_price=Max('predicted_price'),            # Maximum price
        total_predictions=Count('id'),              # Total count
        avg_area=Avg('area_sqft'),                  # Average area
        avg_distance=Avg('distance_to_city_km')      # Average distance
    )
    
    # Calculate total market value of all predictions
    # Loop through all predictions and sum up (price × area) for each
    total_market_value = 0
    for pred in LandPrediction.objects.all():
        total_market_value += pred.predicted_price * pred.area_sqft
    
    # Get 10 most recent predictions
    recent_predictions = LandPrediction.objects.all()[:10]
    
    # Calculate total value for each prediction
    for pred in recent_predictions:
        pred.total_value = pred.predicted_price * pred.area_sqft
    
    # Group predictions by village and calculate average price for each village
    # values('village') groups by village name
    # annotate() adds calculated fields (avg_price, count)
    village_stats = LandPrediction.objects.values('village').annotate(
        avg_price=Avg('predicted_price'),  # Average price for this village
        count=Count('id')                   # Number of predictions for this village
    ).order_by('-avg_price')  # Sort by highest average price first
    
    # Extract village names and prices for chart
    village_labels = [stat['village'] for stat in village_stats]  # List of village names
    village_prices = [float(stat['avg_price']) for stat in village_stats]  # List of prices
    
    # Get top 10 villages by average price
    top_villages = list(village_stats[:10])
    
    # Categorize prices into ranges (Low, Medium, High, Premium)
    # Get all predicted prices
    all_prices = [p.predicted_price for p in LandPrediction.objects.all()]
    
    if all_prices:  # Only if we have prices
        min_p = min(all_prices)  # Find minimum price
        max_p = max(all_prices)  # Find maximum price
        range_size = (max_p - min_p) / 4  # Divide price range into 4 equal parts
        
        # Count how many prices fall into each category
        ranges = {
            'Low': sum(1 for p in all_prices if p < min_p + range_size),           # Lowest 25%
            'Medium': sum(1 for p in all_prices if min_p + range_size <= p < min_p + 2*range_size),  # 25-50%
            'High': sum(1 for p in all_prices if min_p + 2*range_size <= p < min_p + 3*range_size),  # 50-75%
            'Premium': sum(1 for p in all_prices if p >= min_p + 3*range_size)     # Top 25%
        }
        price_ranges = {
            'labels': list(ranges.keys()),  # Category names
            'data': list(ranges.values())   # Count for each category
        }
    else:
        # If no prices, use empty data
        price_ranges = {'labels': ['Low', 'Medium', 'High', 'Premium'], 'data': [0, 0, 0, 0]}
    
    # Get price trends over last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)  # Calculate date 30 days ago
    # Filter predictions from last 30 days, ordered by date
    trend_predictions = LandPrediction.objects.filter(created_at__gte=thirty_days_ago).order_by('created_at')
    
    # Group predictions by date and calculate average price for each day
    from collections import defaultdict
    daily_avg = defaultdict(list)  # Dictionary to store prices for each date
    
    # Loop through predictions and group by date
    for pred in trend_predictions:
        date_key = pred.created_at.date().isoformat()  # Get date as string (e.g., "2025-01-15")
        daily_avg[date_key].append(pred.predicted_price)  # Add price to that date's list
    
    # Sort dates and calculate average price for each day
    trend_dates = sorted(daily_avg.keys())  # List of dates in order
    # For each date, calculate average of all prices on that day
    trend_prices = [sum(daily_avg[date]) / len(daily_avg[date]) for date in trend_dates]
    
    # Find most common land area size
    most_common_area = LandPrediction.objects.values('area_sqft').annotate(
        count=Count('id')  # Count how many times each area appears
    ).order_by('-count').first()  # Get the one with highest count
    
    # Calculate percentage of predictions with electricity
    electricity_count = LandPrediction.objects.filter(electricity_available=True).count()  # Count with electricity
    # Calculate percentage (with electricity / total * 100)
    electricity_percentage = (electricity_count / stats['total_predictions'] * 100) if stats['total_predictions'] > 0 else 0
    
    # Count predictions made in last 30 days
    this_month = timezone.now() - timedelta(days=30)
    active_predictions = LandPrediction.objects.filter(created_at__gte=this_month).count()
    
    # Prepare all data to send to dashboard template
    context = {
        'avg_price': stats['avg_price'] or 0,              # Average price (or 0 if None)
        'min_price': stats['min_price'] or 0,               # Minimum price
        'max_price': stats['max_price'] or 0,               # Maximum price
        'total_predictions': stats['total_predictions'] or 0,  # Total count
        'total_market_value': total_market_value,            # Total market value
        'recent_predictions': recent_predictions,            # Recent predictions
        'village_labels': village_labels,                    # Village names for chart
        'village_prices': village_prices,                   # Prices for chart
        'top_villages': top_villages,                        # Top performing villages
        'price_ranges': price_ranges,                        # Price distribution data
        'trend_data': {'dates': trend_dates, 'prices': trend_prices},  # Trend data for line chart
        'most_common_area': most_common_area['area_sqft'] if most_common_area else 'N/A',  # Most common area
        'avg_distance': round(stats['avg_distance'] or 0, 2),  # Average distance (rounded to 2 decimals)
        'electricity_percentage': round(electricity_percentage, 1),  # Electricity percentage
        'active_predictions': active_predictions             # Predictions this month
    }
    
    # Show dashboard page with all the data
    return render(request, 'land_price_app/dashboard.html', context)

# This function handles user registration (sign up)
def register(request):
    """Handle user registration."""
    # Check if form was submitted
    if request.method == 'POST':
        # Create form with submitted data
        form = CustomUserCreationForm(request.POST)
        
        # Check if form is valid
        if form.is_valid():
            # Save new user to database
            form.save()
            
            # Get the username that was created
            username = form.cleaned_data.get('username')
            
            # Show success message
            messages.success(request, f'Account created for {username}! You can now login.')
            
            # Redirect to login page
            return redirect('land_price_app:login')
    else:
        # If not POST (first time loading page), show empty form
        form = CustomUserCreationForm()
    
    # Show registration page with form
    return render(request, 'land_price_app/register.html', {'form': form})

# Simple function to show about page
def about(request):
    return render(request, 'land_price_app/about.html')

# Simple function to show FAQ page
def faq(request):
    return render(request, 'land_price_app/faq.html')

# This function shows list of all blog posts
def blog(request):
    """Display blog posts list."""
    from django.core.paginator import Paginator  # For splitting posts into pages
    
    # Get all non-featured posts, ordered by newest first
    posts = BlogPost.objects.filter(featured=False).order_by('-created_at')
    
    # Get the most recent featured post (if any)
    featured_post = BlogPost.objects.filter(featured=True).order_by('-created_at').first()
    
    # Split posts into pages (9 posts per page)
    paginator = Paginator(posts, 9)
    
    # Get which page number user wants (from URL, e.g., ?page=2)
    page_number = request.GET.get('page')
    
    # Get the requested page
    blog_posts = paginator.get_page(page_number)
    
    # Prepare data for template
    context = {
        'blog_posts': blog_posts,      # Posts for current page
        'featured_post': featured_post  # Featured post (if any)
    }
    
    # Show blog listing page
    return render(request, 'land_price_app/blog.html', context)

# This function shows a single blog post in detail
def blog_detail(request, slug):
    """Display individual blog post."""
    from django.shortcuts import get_object_or_404  # Get object or show 404 error
    
    # Find blog post by slug (URL-friendly name)
    # If not found, show 404 error page
    post = get_object_or_404(BlogPost, slug=slug)
    
    # Increase view count by 1
    post.views += 1
    # Save only the views field (more efficient than saving entire object)
    post.save(update_fields=['views'])
    
    # Find related posts (same category, but not the current post)
    # Get 2 most recent posts from same category
    related_posts = BlogPost.objects.filter(
        category=post.category  # Same category
    ).exclude(id=post.id).order_by('-created_at')[:2]  # Exclude current, newest first, limit 2
    
    # Prepare data for template
    context = {
        'post': post,                    # The blog post
        'related_posts': related_posts   # Related posts
    }
    
    # Show blog detail page
    return render(request, 'land_price_app/blog_detail.html', context)

# Custom logout function (handles both GET and POST requests)
def logout_view(request):
    """Custom logout view that handles both GET and POST requests."""
    # Check if user is logged in
    if request.user.is_authenticated:
        # Log out the user
        logout(request)
        
        # Show success message
        messages.success(request, 'You have been successfully logged out.')
    
    # Redirect to home page
    return redirect('land_price_app:home')

# This function handles contact form submission
def contact(request):
    # Check if form was submitted
    if request.method == 'POST':
        # Get form data (strip removes extra spaces)
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Check if all fields are filled
        if name and email and message:
            # Save message to database
            ContactMessage.objects.create(name=name, email=email, message=message)
            
            # Show success message
            messages.success(request, 'Thanks! Your message has been received.')
            
            # Go back to contact page
            return redirect('land_price_app:contact')
        
        # If fields are empty, show error
        messages.error(request, 'Please fill all fields correctly.')
    
    # Show contact page (first time or after error)
    return render(request, 'land_price_app/contact.html')
