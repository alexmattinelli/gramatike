// Shared utility functions
// Used across multiple pages

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Format date to Brazilian Portuguese
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Handle API errors
 */
function handleApiError(error, defaultMessage = 'Erro ao processar requisição') {
    console.error('API Error:', error);
    showNotification(defaultMessage, 'error');
}

/**
 * Check if user is authenticated
 */
async function checkAuth() {
    try {
        const response = await fetch('/api/users/me');
        return response.ok;
    } catch (error) {
        return false;
    }
}

/**
 * Redirect to login if not authenticated
 */
async function requireAuth() {
    const isAuth = await checkAuth();
    if (!isAuth) {
        window.location.href = '/login';
    }
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        formatDate,
        handleApiError,
        checkAuth,
        requireAuth
    };
}
