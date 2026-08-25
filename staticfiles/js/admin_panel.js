// Dedicated Admin Panel Frontend Controller

function showAdminToast(message, type = 'info') {
    const toastEl = document.getElementById('admin-toast');
    const toastBody = document.getElementById('admin-toast-msg');
    if (!toastEl || !toastBody) return;

    toastEl.className = `toast align-items-center text-white border-0 bg-${type === 'error' ? 'danger' : (type === 'success' ? 'success' : 'primary')}`;
    toastBody.innerHTML = message;
    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
    toast.show();
}

function getAdminAccessToken() {
    return localStorage.getItem('access_token');
}

function getAdminRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function getAdminRole() {
    return localStorage.getItem('user_role');
}

function logoutAdmin() {
    const refresh = getAdminRefreshToken();
    if (refresh) {
        fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAdminAccessToken()}`
            },
            body: JSON.stringify({ refresh })
        }).catch(() => {});
    }
    localStorage.clear();
    window.location.href = '/admin/login/';
}

function requireAdminRole() {
    const token = getAdminAccessToken();
    const role = getAdminRole();

    if (!token || !role || (role !== 'ADMIN' && role !== 'AUTHOR')) {
        showAdminToast('Unauthorized access. Admin privileges required.', 'error');
        window.location.href = '/admin/login/';
        return false;
    }
    return true;
}

async function refreshAdminToken() {
    const refresh = getAdminRefreshToken();
    if (!refresh) return false;

    try {
        const res = await fetch('/api/auth/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('access_token', data.access);
            return true;
        }
    } catch (e) {
        console.error('Admin token refresh failed:', e);
    }
    return false;
}

async function fetchAdminApi(url, options = {}) {
    options.headers = options.headers || {};
    let token = getAdminAccessToken();

    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }

    let response = await fetch(url, options);

    if (response.status === 401 && getAdminRefreshToken()) {
        const refreshed = await refreshAdminToken();
        if (refreshed) {
            options.headers['Authorization'] = `Bearer ${getAdminAccessToken()}`;
            response = await fetch(url, options);
        } else {
            logoutAdmin();
        }
    }

    return response;
}

async function loadAdminDashboard() {
    if (!requireAdminRole()) return;

    try {
        const res = await fetchAdminApi('/api/dashboard/');
        const data = await res.json();
        if (res.ok && data.success) {
            const s = data.data;
            if (document.getElementById('stat-total-books')) document.getElementById('stat-total-books').textContent = s.total_books || 0;
            if (document.getElementById('stat-avail-books')) document.getElementById('stat-avail-books').textContent = s.available_books || 0;
            if (document.getElementById('stat-borrowed-books')) document.getElementById('stat-borrowed-books').textContent = s.borrowed_books || 0;
            if (document.getElementById('stat-total-users')) document.getElementById('stat-total-users').textContent = s.total_users || 0;
            if (document.getElementById('stat-active-users')) document.getElementById('stat-active-users').textContent = s.active_users || 0;
            if (document.getElementById('stat-overdue-books')) document.getElementById('stat-overdue-books').textContent = s.overdue_books || 0;
            if (document.getElementById('stat-total-fines')) document.getElementById('stat-total-fines').textContent = `$${(s.total_fines || 0).toFixed(2)}`;
        }
    } catch (e) {
        console.error('Error loading admin stats:', e);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
}
