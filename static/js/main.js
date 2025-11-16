/**
 * MediLocator Main JavaScript
 * commit: chore: add core JavaScript utilities and interactive features
 */

// Session timeout management (30 minutes)
let sessionTimeout;
let warningTimeout;
const SESSION_DURATION = 30 * 60 * 1000; // 30 minutes
const WARNING_TIME = 5 * 60 * 1000; // 5 minutes before timeout

function resetSessionTimer() {
    clearTimeout(sessionTimeout);
    clearTimeout(warningTimeout);
    
    // Show warning 5 minutes before timeout
    warningTimeout = setTimeout(() => {
        showSessionWarning();
    }, SESSION_DURATION - WARNING_TIME);
    
    // Logout after 30 minutes
    sessionTimeout = setTimeout(() => {
        window.location.href = '/logout/';
    }, SESSION_DURATION);
}

function showSessionWarning() {
    if (confirm('Your session will expire in 5 minutes due to inactivity. Click OK to stay logged in.')) {
        resetSessionTimer();
        // Ping server to keep session alive
        fetch('/api/keep-alive/', { method: 'POST' });
    }
}

// Reset timer on user activity
if (document.body.classList.contains('authenticated')) {
    ['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetSessionTimer);
    });
    resetSessionTimer();
}

// Toast notification system
function showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast alert alert-${type} slide-in-right`;
    toast.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; cursor: pointer; margin-left: 1rem;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        const errorElement = input.nextElementSibling;
        
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = 'var(--error-dark)';
            
            if (errorElement && errorElement.classList.contains('form-error')) {
                errorElement.textContent = 'This field is required';
            } else {
                const error = document.createElement('div');
                error.className = 'form-error';
                error.textContent = 'This field is required';
                input.parentNode.insertBefore(error, input.nextSibling);
            }
        } else {
            input.style.borderColor = '';
            if (errorElement && errorElement.classList.contains('form-error')) {
                errorElement.remove();
            }
        }
    });
    
    return isValid;
}

// Email validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Phone validation
function validatePhone(phone) {
    const re = /^\+?1?\d{9,15}$/;
    return re.test(phone);
}

// Loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading-spinner"></div>';
        element.style.pointerEvents = 'none';
    }
}

function hideLoading(elementId, originalContent) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = originalContent;
        element.style.pointerEvents = 'auto';
    }
}

// Modal utilities
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        closeModal(event.target.id);
    }
});

// Escape key to close modal
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => {
            if (modal.style.display === 'flex') {
                closeModal(modal.id);
            }
        });
    }
});

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success', 2000);
    }).catch(() => {
        showToast('Failed to copy', 'error', 2000);
    });
}

// Debounce function for search/input handlers
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Calculate distance between two coordinates (Haversine formula)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of Earth in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c;
    
    return distance.toFixed(2); // Returns distance in km
}

// Get user's current location
function getCurrentLocation(callback) {
    if (navigator.geolocation) {
        showToast('Getting your location...', 'info', 2000);
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                callback({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
                showToast('Location found!', 'success', 2000);
            },
            (error) => {
                let message = 'Unable to get location';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        message = 'Location permission denied. Please enable location access.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = 'Location information unavailable';
                        break;
                    case error.TIMEOUT:
                        message = 'Location request timed out';
                        break;
                }
                showToast(message, 'error', 5000);
            }
        );
    } else {
        showToast('Geolocation is not supported by your browser', 'error', 5000);
    }
}

// File upload preview
function previewImage(input, previewElementId) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewElementId);
            if (preview) {
                if (preview.tagName === 'IMG') {
                    preview.src = e.target.result;
                } else {
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100%; border-radius: var(--radius-md);">`;
                }
            }
        };
        reader.readAsDataURL(file);
    }
}

// Check file size
function validateFileSize(input, maxSizeMB = 5) {
    const file = input.files[0];
    if (file) {
        const sizeMB = file.size / (1024 * 1024);
        if (sizeMB > maxSizeMB) {
            showToast(`File size must be less than ${maxSizeMB}MB`, 'error', 5000);
            input.value = '';
            return false;
        }
    }
    return true;
}

// Smooth scroll to element
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// AJAX helper with CSRF token
function ajaxRequest(url, method = 'GET', data = null) {
    const csrftoken = getCookie('csrftoken');
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred. Please try again.', 'error', 5000);
            throw error;
        });
}

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize tooltips (if using)
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Add authentication class to body if user is logged in
    const navbarNav = document.querySelector('.navbar-nav');
    if (navbarNav && navbarNav.innerHTML.includes('Logout')) {
        document.body.classList.add('authenticated');
    }
    
    console.log('MediLocator initialized successfully!');
});

// Export functions for use in other scripts
window.MediLocator = {
    showToast,
    validateForm,
    validateEmail,
    validatePhone,
    showLoading,
    hideLoading,
    openModal,
    closeModal,
    copyToClipboard,
    debounce,
    formatCurrency,
    formatDate,
    calculateDistance,
    getCurrentLocation,
    previewImage,
    validateFileSize,
    smoothScrollTo,
    ajaxRequest,
    getCookie
};
