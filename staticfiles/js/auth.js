// Centralized Authentication & HTTP Request Service

function showToast(message, type = 'info') {
    const toastEl = document.getElementById('app-toast');
    const toastBody = document.getElementById('toast-message');
    if (!toastEl || !toastBody) return;

    toastEl.className = `toast align-items-center text-white border-0 bg-${type === 'error' ? 'danger' : type}`;
    toastBody.innerHTML = message;
    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
    toast.show();
}

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function getUserRole() {
    return localStorage.getItem('user_role');
}

function logoutUser() {
    const refresh = getRefreshToken();
    if (refresh) {
        fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAccessToken()}`
            },
            body: JSON.stringify({ refresh })
        }).catch(() => {});
    }
    localStorage.clear();
    window.location.href = '/login/';
}

function requireRole(expectedRole) {
    const token = getAccessToken();
    const role = getUserRole();
    if (!token || !role) {
        window.location.href = '/login/';
        return false;
    }
    if (expectedRole && role !== expectedRole) {
        window.location.href = role === 'AUTHOR' ? '/author/dashboard/' : '/member/dashboard/';
        return false;
    }
    return true;
}

async function refreshToken() {
    const refresh = getRefreshToken();
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
        console.error('Token refresh failed:', e);
    }
    return false;
}

async function fetchWithAuth(url, options = {}) {
    options.headers = options.headers || {};
    let token = getAccessToken();

    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }

    let response = await fetch(url, options);

    // Automatic token refresh handling on 401
    if (response.status === 401 && getRefreshToken()) {
        const refreshed = await refreshToken();
        if (refreshed) {
            options.headers['Authorization'] = `Bearer ${getAccessToken()}`;
            response = await fetch(url, options);
        } else {
            logoutUser();
        }
    }

    return response;
}

function setupNavbar() {
    const role = getUserRole();
    const navLinks = document.getElementById('nav-links');
    const profileWidget = document.getElementById('user-profile-widget');

    if (!navLinks) return;

    if (!role) {
        navLinks.innerHTML = `
            <li class="nav-item"><a class="nav-link" href="/login/">Login</a></li>
            <li class="nav-item"><a class="nav-link" href="/register/">Register</a></li>
        `;
        if (profileWidget) profileWidget.classList.add('d-none');
        return;
    }

    if (profileWidget) {
        profileWidget.classList.remove('d-none');
        document.getElementById('user-role-badge').textContent = role;
        document.getElementById('user-display-name').textContent = localStorage.getItem('user_name') || 'User';
    }

    if (role === 'AUTHOR') {
        navLinks.innerHTML = `
            <li class="nav-item"><a class="nav-link" href="/author/dashboard/"><i class="fa-solid fa-gauge me-1"></i> Dashboard</a></li>
            <li class="nav-item"><a class="nav-link" href="/author/books/"><i class="fa-solid fa-book me-1"></i> My Books</a></li>
            <li class="nav-item"><a class="nav-link" href="/author/books/create/"><i class="fa-solid fa-plus me-1"></i> Add Book</a></li>
        `;
    } else if (role === 'MEMBER') {
        navLinks.innerHTML = `
            <li class="nav-item"><a class="nav-link" href="/member/dashboard/"><i class="fa-solid fa-gauge me-1"></i> Dashboard</a></li>
            <li class="nav-item"><a class="nav-link" href="/member/books/"><i class="fa-solid fa-book-open me-1"></i> Browse Books</a></li>
            <li class="nav-item"><a class="nav-link" href="/member/borrowed/"><i class="fa-solid fa-hand-holding-hand me-1"></i> My Loans</a></li>
            <li class="nav-item"><a class="nav-link text-warning" href="/member/overdue/"><i class="fa-solid fa-triangle-exclamation me-1"></i> Overdue</a></li>
            <li class="nav-item"><a class="nav-link" href="/member/history/"><i class="fa-solid fa-clock-rotate-left me-1"></i> History</a></li>
        `;
    }
}

document.addEventListener('DOMContentLoaded', setupNavbar);
