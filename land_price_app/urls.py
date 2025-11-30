# Import URL routing function
from django.urls import path
# Import Django's built-in authentication views (login, logout, etc.)
from django.contrib.auth import views as auth_views
# Import our custom views (functions that handle requests)
from . import views

# This is the app name - used to identify URLs (e.g., 'land_price_app:home')
app_name = 'land_price_app'

# This list defines all URL patterns (which URL goes to which view function)
urlpatterns = [
    # Home page - empty string '' means root URL (e.g., http://localhost:8000/)
    # When user visits root URL, call views.home function
    path('', views.home, name='home'),
    
    # Result page - shows prediction results
    # URL: /result/
    path('result/', views.result, name='result'),
    
    # Dashboard page - shows analytics (requires login)
    # URL: /dashboard/
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # About page - information about the project
    # URL: /about/
    path('about/', views.about, name='about'),
    
    # Contact page - contact form
    # URL: /contact/
    path('contact/', views.contact, name='contact'),
    
    # Blog listing page - shows all blog posts
    # URL: /blog/
    path('blog/', views.blog, name='blog'),
    
    # Blog detail page - shows single blog post
    # <slug:slug> means capture the slug from URL (e.g., /blog/how-to-buy-land/)
    # slug is URL-friendly version of title
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # FAQ page - frequently asked questions
    # URL: /faq/
    path('faq/', views.faq, name='faq'),
    
    # Login page - user login form
    # Uses Django's built-in LoginView, but with custom template
    # URL: /login/
    path('login/', auth_views.LoginView.as_view(template_name='land_price_app/login.html'), name='login'),
    
    # Logout page - logs out user
    # URL: /logout/
    path('logout/', views.logout_view, name='logout'),
    
    # Registration page - user sign up form
    # URL: /register/
    path('register/', views.register, name='register'),
]
