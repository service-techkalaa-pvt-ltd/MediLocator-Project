from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import UserProfile, Pharmacy, Medicine, Inventory, Feedback
from django.utils import timezone
from datetime import timedelta

# Admin Check Decorator
def is_admin(user):
    """Check if user is admin (staff or has ADMIN role)"""
    if not user.is_authenticated:
        return False
    return user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'ADMIN')

# ==================== AUTHENTICATION ====================

def admin_login(request):
    """Custom admin login page"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard_main')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if is_admin(user):
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('admin_dashboard_main')
            else:
                messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'admin/adminml.html')

def admin_register(request):
    """Admin registration page - open registration"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard_main')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.save()
            
            # Create admin profile
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'ADMIN'})
            
            messages.success(request, f'Admin account created successfully! Please login.')
            return redirect('admin_login')
    
    return render(request, 'admin/adminregister.html')

@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')

# ==================== DASHBOARD ====================

@login_required
@user_passes_test(is_admin)
def admin_dashboard_main(request):
    """Main admin dashboard with real-time data"""
    # Get all real data from database
    total_users = User.objects.count()
    total_pharmacies = Pharmacy.objects.count()
    total_medicines = Medicine.objects.count()
    total_feedback = Feedback.objects.count()
    pending_pharmacies = Pharmacy.objects.filter(verified=False).count()
    verified_pharmacies = Pharmacy.objects.filter(verified=True).count()
    
    # Recent data
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:5]
    recent_pharmacies = Pharmacy.objects.order_by('-created_at')[:5]
    recent_feedback = Feedback.objects.order_by('-submitted_at')[:5]
    
    # Pharmacy statistics by city
    pharmacies_by_city = Pharmacy.objects.values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_users': total_users,
        'total_pharmacies': total_pharmacies,
        'total_medicines': total_medicines,
        'total_feedback': total_feedback,
        'pending_pharmacies': pending_pharmacies,
        'verified_pharmacies': verified_pharmacies,
        'recent_users': recent_users,
        'recent_pharmacies': recent_pharmacies,
        'recent_feedback': recent_feedback,
        'pharmacies_by_city': pharmacies_by_city,
        'admin_user': request.user,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    """System reports and analytics"""
    # Date filters
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User statistics
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    new_users_month = User.objects.filter(date_joined__date__gte=month_ago).count()
    
    # Pharmacy statistics
    pharmacies_by_verified = {
        'verified': Pharmacy.objects.filter(verified=True).count(),
        'unverified': Pharmacy.objects.filter(verified=False).count(),
    }
    
    # Medicine statistics
    total_medicines = Medicine.objects.count()
    medicines_in_stock = Inventory.objects.filter(quantity__gt=0).values('medicine').distinct().count()
    
    # Feedback statistics
    total_feedback = Feedback.objects.count()
    recent_feedback = Feedback.objects.order_by('-submitted_at')[:10]
    
    context = {
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'new_users_month': new_users_month,
        'pharmacies_by_verified': pharmacies_by_verified,
        'total_medicines': total_medicines,
        'medicines_in_stock': medicines_in_stock,
        'total_feedback': total_feedback,
        'recent_feedback': recent_feedback,
        'admin_user': request.user,
    }
    return render(request, 'admin/reports.html', context)

# ==================== USER MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """List all users with search and filter"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Filter by role
    role = request.GET.get('role', '')
    if role:
        if role == 'admin':
            users = users.filter(Q(is_staff=True) | Q(profile__role='ADMIN'))
        elif role == 'pharmacy':
            users = users.filter(profile__role='PHARMACY')
        elif role == 'customer':
            users = users.filter(profile__role='CUSTOMER')
    
    # Filter by active status
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 50)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    context = {
        'users': users_page,
        'search': search,
        'role': role,
        'status': status,
        'admin_user': request.user,
    }
    return render(request, 'admin/users.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_edit(request, user_id):
    """Edit user details"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Update password if provided
        new_password = request.POST.get('password')
        if new_password and new_password.strip():
            user.set_password(new_password)
            messages.info(request, 'Password updated successfully!')
        
        user.save()
        
        messages.success(request, f'User {user.username} updated successfully!')
        return redirect('admin_users')
    
    return render(request, 'admin/user_edit.html', {'user_obj': user, 'admin_user': request.user})

@login_required
@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    """Delete user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('admin_users')
    
    return render(request, 'admin/user_delete_confirm.html', {'user_obj': user, 'admin_user': request.user})

# ==================== PHARMACY MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_pharmacies(request):
    """List all pharmacies with search and filter"""
    pharmacies = Pharmacy.objects.all().order_by('-created_at')
    
    # Get unique cities for filter dropdown
    cities = Pharmacy.objects.values_list('city', flat=True).distinct().order_by('city')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        pharmacies = pharmacies.filter(
            Q(name__icontains=search) |
            Q(address__icontains=search) |
            Q(city__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Filter by city
    city_filter = request.GET.get('city', '')
    if city_filter:
        pharmacies = pharmacies.filter(city=city_filter)
    
    # Filter by verified status
    verified_filter = request.GET.get('verified', '')
    if verified_filter:
        if verified_filter == 'true':
            pharmacies = pharmacies.filter(verified=True)
        elif verified_filter == 'false':
            pharmacies = pharmacies.filter(verified=False)
    
    # Pagination - show 100 pharmacies per page (or set to a very high number to show all)
    paginator = Paginator(pharmacies, 100)
    page = request.GET.get('page', 1)
    pharmacies_page = paginator.get_page(page)
    
    context = {
        'pharmacies': pharmacies_page,
        'search': search,
        'verified_filter': verified_filter,
        'city_filter': city_filter,
        'cities': cities,
        'admin_user': request.user,
    }
    return render(request, 'admin/pharmacies.html', context)

@login_required
@user_passes_test(is_admin)
def admin_pharmacy_add(request):
    """Add new pharmacy"""
    if request.method == 'POST':
        pharmacy = Pharmacy(
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
            verified=True  # Admin-added pharmacies are auto-verified
        )
        pharmacy.save()
        
        messages.success(request, f'Pharmacy {pharmacy.name} added successfully!')
        return redirect('admin_pharmacies')
    
    return render(request, 'admin/pharmacy_form.html', {'action': 'Add', 'admin_user': request.user})

@login_required
@user_passes_test(is_admin)
def admin_pharmacy_edit(request, pharmacy_id):
    """Edit pharmacy details"""
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    
    if request.method == 'POST':
        pharmacy.name = request.POST.get('name')
        pharmacy.address = request.POST.get('address')
        pharmacy.city = request.POST.get('city')
        pharmacy.state = request.POST.get('state')
        pharmacy.pincode = request.POST.get('pincode')
        pharmacy.phone = request.POST.get('phone')
        pharmacy.email = request.POST.get('email')
        pharmacy.latitude = request.POST.get('latitude')
        pharmacy.longitude = request.POST.get('longitude')
        pharmacy.save()
        
        messages.success(request, f'Pharmacy {pharmacy.name} updated successfully!')
        return redirect('admin_pharmacies')
    
    return render(request, 'admin/pharmacy_form.html', {'pharmacy': pharmacy, 'action': 'Edit', 'admin_user': request.user})

@login_required
@user_passes_test(is_admin)
def admin_pharmacy_delete(request, pharmacy_id):
    """Delete pharmacy"""
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    
    if request.method == 'POST':
        name = pharmacy.name
        pharmacy.delete()
        messages.success(request, f'Pharmacy {name} deleted successfully!')
        return redirect('admin_pharmacies')
    
    return render(request, 'admin/pharmacy_delete_confirm.html', {'pharmacy': pharmacy, 'admin_user': request.user})

@login_required
@user_passes_test(is_admin)
def admin_pharmacy_verify(request, pharmacy_id):
    """Verify or reject pharmacy"""
    pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            pharmacy.verified = True
            pharmacy.save()
            messages.success(request, f'Pharmacy {pharmacy.name} has been verified!')
        elif action == 'reject':
            pharmacy.verified = False
            pharmacy.save()
            messages.warning(request, f'Pharmacy {pharmacy.name} has been unverified.')
        
        return redirect('admin_pharmacies')
    
    return render(request, 'admin/pharmacy_verify.html', {'pharmacy': pharmacy, 'admin_user': request.user})

# ==================== MEDICINE MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_medicines(request):
    """List all medicines with search and filters"""
    medicines = Medicine.objects.all().order_by('name')
    
    # Get unique categories for filter dropdown
    categories = Medicine.objects.values_list('category', flat=True).distinct().order_by('category')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        medicines = medicines.filter(
            Q(name__icontains=search) |
            Q(category__icontains=search) |
            Q(generic_name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        medicines = medicines.filter(category=category_filter)
    
    # Pagination
    paginator = Paginator(medicines, 50)
    page = request.GET.get('page', 1)
    medicines_page = paginator.get_page(page)
    
    context = {
        'medicines': medicines_page,
        'search': search,
        'category_filter': category_filter,
        'categories': categories,
        'admin_user': request.user,
    }
    return render(request, 'admin/medicines.html', context)

@login_required
@user_passes_test(is_admin)
def admin_medicine_add(request):
    """Add new medicine"""
    if request.method == 'POST':
        medicine = Medicine(
            name=request.POST.get('name'),
            generic_name=request.POST.get('generic_name', ''),
            category=request.POST.get('category', ''),
            description=request.POST.get('description', ''),
            common_doses=request.POST.get('common_doses', '')
        )
        medicine.save()
        
        messages.success(request, f'Medicine {medicine.name} added successfully!')
        return redirect('admin_medicines')
    
    return render(request, 'admin/medicine_form.html', {'action': 'Add', 'admin_user': request.user})

@login_required
@user_passes_test(is_admin)
def admin_medicine_edit(request, medicine_id):
    """Edit medicine details"""
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        medicine.name = request.POST.get('name')
        medicine.generic_name = request.POST.get('generic_name', '')
        medicine.category = request.POST.get('category', '')
        medicine.description = request.POST.get('description', '')
        medicine.common_doses = request.POST.get('common_doses', '')
        medicine.save()
        
        messages.success(request, f'Medicine {medicine.name} updated successfully!')
        return redirect('admin_medicines')
    
    return render(request, 'admin/medicine_form.html', {'medicine': medicine, 'action': 'Edit', 'admin_user': request.user})

@login_required
@user_passes_test(is_admin)
def admin_medicine_delete(request, medicine_id):
    """Delete medicine"""
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        name = medicine.name
        medicine.delete()
        messages.success(request, f'Medicine {name} deleted successfully!')
        return redirect('admin_medicines')
    
    return render(request, 'admin/medicine_delete_confirm.html', {'medicine': medicine, 'admin_user': request.user})

# ==================== FEEDBACK MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_feedback(request):
    """List all feedback"""
    feedbacks = Feedback.objects.all().order_by('-id')
    
    # Pagination
    paginator = Paginator(feedbacks, 20)
    page = request.GET.get('page', 1)
    feedbacks_page = paginator.get_page(page)
    
    context = {
        'feedbacks': feedbacks_page,
        'admin_user': request.user,
    }
    return render(request, 'admin/feedback.html', context)

@login_required
@user_passes_test(is_admin)
def admin_feedback_delete(request, feedback_id):
    """Delete feedback"""
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    if request.method == 'POST':
        feedback.delete()
        messages.success(request, 'Feedback deleted successfully!')
        return redirect('admin_feedback')
    
    # If GET request, show confirmation page or redirect
    messages.warning(request, 'Invalid request method.')
    return redirect('admin_feedback')
