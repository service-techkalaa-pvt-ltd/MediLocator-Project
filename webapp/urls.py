from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # CUSTOM ADMIN PANEL (Must be FIRST to avoid conflicts with Django admin)
    path('admin-ml/', admin_views.admin_login, name='admin_login'),
    path('admin-ml/register/', admin_views.admin_register, name='admin_register'),
    path('admin-ml/logout/', admin_views.admin_logout, name='admin_logout'),
    path('admin-ml/dashboard/', admin_views.admin_dashboard_main, name='admin_dashboard_main'),
    path('admin-ml/reports/', admin_views.admin_reports, name='admin_reports'),
    path('admin-ml/users/', admin_views.admin_users, name='admin_users'),
    path('admin-ml/users/<int:user_id>/edit/', admin_views.admin_user_edit, name='admin_user_edit'),
    path('admin-ml/users/<int:user_id>/delete/', admin_views.admin_user_delete, name='admin_user_delete'),
    path('admin-ml/pharmacies/', admin_views.admin_pharmacies, name='admin_pharmacies'),
    path('admin-ml/pharmacies/add/', admin_views.admin_pharmacy_add, name='admin_pharmacy_add'),
    path('admin-ml/pharmacies/<int:pharmacy_id>/edit/', admin_views.admin_pharmacy_edit, name='admin_pharmacy_edit'),
    path('admin-ml/pharmacies/<int:pharmacy_id>/delete/', admin_views.admin_pharmacy_delete, name='admin_pharmacy_delete'),
    path('admin-ml/pharmacies/<int:pharmacy_id>/verify/', admin_views.admin_pharmacy_verify, name='admin_pharmacy_verify'),
    path('admin-ml/medicines/', admin_views.admin_medicines, name='admin_medicines'),
    path('admin-ml/medicines/add/', admin_views.admin_medicine_add, name='admin_medicine_add'),
    path('admin-ml/medicines/<int:medicine_id>/edit/', admin_views.admin_medicine_edit, name='admin_medicine_edit'),
    path('admin-ml/medicines/<int:medicine_id>/delete/', admin_views.admin_medicine_delete, name='admin_medicine_delete'),
    path('admin-ml/feedback/', admin_views.admin_feedback, name='admin_feedback'),
    path('admin-ml/feedback/<int:feedback_id>/delete/', admin_views.admin_feedback_delete, name='admin_feedback_delete'),
    
    # Authentication
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    
    # Main pages
    path('', views.home, name="home"),
    path("home1", views.home1, name='home1'),
    path("predict", views.predict, name='predict'),
    path("search-results/", views.search_results_page, name='search_results_page'),
    
    # Prescription & Search
    path('prescription-scanner/', views.prescription_scanner, name='prescription_scanner'),  # Upload prescription page
    path('api/process-prescription/', views.process_prescription, name='process_prescription'),  # OCR processing endpoint
    path('api/search-medicines-manual/', views.search_medicines_manual, name='search_medicines_manual'),  # Manual medicine search
    path('search/manual/', views.search_manual_page, name='search_manual_page'),
    path('search/gps/', views.search_gps_page, name='search_gps_page'),
    
    # User & Info
    path('profile/', views.user_profile, name='user_profile'),
    path("feedback/", views.feedback_view, name="feedback"),
    path("about_us/", views.about_us, name="about_us"),
    
    # Dashboards
    path('pharmacy/dashboard/', views.pharmacy_dashboard, name='pharmacy_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # PHARMACY OWNER PORTAL
    path('pharmacy/register/', views.pharmacy_register, name='pharmacy_register'),
    path('pharmacy/login/', views.pharmacy_login, name='pharmacy_login'),
    path('pharmacy/logout/', views.pharmacy_logout, name='pharmacy_logout'),
    path('pharmacy/medicines/', views.pharmacy_medicines, name='pharmacy_medicines'),
    path('pharmacy/add-medicine/', views.pharmacy_add_medicine, name='pharmacy_add_medicine'),
    path('pharmacy/bulk-upload/', views.pharmacy_bulk_upload, name='pharmacy_bulk_upload'),
    path('pharmacy/bulk-upload-confirm/', views.pharmacy_bulk_upload_confirm, name='pharmacy_bulk_upload_confirm'),
    path('pharmacy/download-template/', views.pharmacy_download_template, name='pharmacy_download_template'),
    path('pharmacy/edit-medicine/<int:inventory_id>/', views.pharmacy_edit_medicine, name='pharmacy_edit_medicine'),
    path('pharmacy/delete-medicine/<int:inventory_id>/', views.pharmacy_delete_medicine, name='pharmacy_delete_medicine'),
    path('pharmacy/settings/', views.pharmacy_settings, name='pharmacy_settings'),
    path('pharmacy/orders/', views.pharmacy_orders, name='pharmacy_orders'),
    path('pharmacy/analytics/', views.pharmacy_analytics, name='pharmacy_analytics'),
    
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
    
    # Chatbot
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
    path('chatbot-response/', views.chatbot_response, name='chatbot_response'),
]



