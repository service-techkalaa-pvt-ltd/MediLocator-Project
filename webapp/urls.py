from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    
    # Main pages
    path('', views.home, name="home"),
    path("home1", views.home1, name='home1'),
    path("predict", views.predict, name='predict'),
    path("search-results/", views.search_results_page, name='search_results_page'),
    
    # Manual and GPS Search Pages
    path('search/manual/', views.search_manual_page, name='search_manual_page'),
    path('search/gps/', views.search_gps_page, name='search_gps_page'),
    
    # Prescription & Search
    path('prescription-scanner/', views.prescription_scanner, name='prescription_scanner'),  # Upload prescription page
    
    # Chatbot
    path('chatbot/', views.chatbot_page, name='chatbot'),
    path('chatbot1/', views.chatbot_page, name='chatbot_page'),
    path("chatbot-response/", views.chatbot_response, name="chatbot-response"),
    
    # User & Info
    path('profile/', views.user_profile, name='user_profile'),
    path("feedback/", views.feedback_view, name="feedback"),
    path("about_us/", views.about_us, name="about_us"),
    
    # Dashboards
    path('pharmacy/dashboard/', views.pharmacy_dashboard, name='pharmacy_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # API endpoints
    path('api/keep-alive/', views.keep_alive, name='keep_alive'),
    path('api/search-pharmacies/', views.search_pharmacies, name='search_pharmacies'),
    path('api/search-medicines/', views.search_medicines, name='search_medicines'),
    path('api/search-by-city/', views.search_by_city, name='search_by_city'),
    path('api/get-medicines/', views.get_medicine_list, name='get_medicine_list'),
    path('api/medicine-detail/<int:medicine_id>/', views.get_medicine_detail, name='get_medicine_detail'),
    path('api/trending-medicines/', views.get_trending_medicines, name='trending_medicines'),
    path('api/all-pharmacies/', views.search_all_pharmacies, name='all_pharmacies'),
    path('api/all-medicines/', views.search_all_medicines, name='all_medicines'),
    path('api/locations-list/', views.search_locations_list, name='locations_list'),
    
    # New Manual and GPS Search APIs
    path('api/search-manual/', views.search_manual, name='search_manual_api'),
    path('api/search-gps/', views.search_gps, name='search_gps_api'),
]



