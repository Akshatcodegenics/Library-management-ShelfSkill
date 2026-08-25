// User Library App Frontend Controller

function showUserToast(message, type = 'info') {
    const toastEl = document.getElementById('user-toast');
    const toastBody = document.getElementById('user-toast-msg');
    if (!toastEl || !toastBody) return;

    toastEl.className = `toast align-items-center text-white border-0 bg-${type === 'error' ? 'danger' : (type === 'success' ? 'success' : 'primary')}`;
    toastBody.innerHTML = message;
    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
    toast.show();
}

function getUserAccessToken() {
    return localStorage.getItem('access_token');
}

function getUserRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function getUserRole() {
    return localStorage.getItem('user_role');
}

function logoutUserApp() {
    const refresh = getUserRefreshToken();
    if (refresh) {
        fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getUserAccessToken()}`
            },
            body: JSON.stringify({ refresh })
        }).catch(() => {});
    }
    localStorage.clear();
    window.location.href = '/login/';
}

async function refreshUserToken() {
    const refresh = getUserRefreshToken();
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

async function fetchUserApi(url, options = {}) {
    options.headers = options.headers || {};
    let token = getUserAccessToken();

    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }

    let response = await fetch(url, options);

    if (response.status === 401 && getUserRefreshToken()) {
        const refreshed = await refreshUserToken();
        if (refreshed) {
            options.headers['Authorization'] = `Bearer ${getUserAccessToken()}`;
            response = await fetch(url, options);
        }
    }

    return response;
}

function setupUserNavbar() {
    const role = getUserRole();
    const token = getUserAccessToken();
    const navLinks = document.getElementById('user-nav-links');
    const authWidget = document.getElementById('user-auth-widget');

    if (!navLinks || !authWidget) return;

    if (token && role) {
        // Authenticated Navbar
        navLinks.innerHTML = `
            <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
            <li class="nav-item"><a class="nav-link text-warning" href="/shelf/"><i class="fa-solid fa-book-shelf me-1"></i> Library Shelves</a></li>
            <li class="nav-item"><a class="nav-link" href="/books/">Browse Books</a></li>
            <li class="nav-item"><a class="nav-link" href="/my-borrowed/">My Borrowed</a></li>
            <li class="nav-item"><a class="nav-link" href="/history/">Loan History</a></li>
            <li class="nav-item"><a class="nav-link" href="/profile/">My Profile</a></li>
        `;


        const name = localStorage.getItem('user_name') || 'User';
        authWidget.innerHTML = `
            <div class="dropdown">
                <button class="btn btn-outline-light dropdown-toggle rounded-pill px-3" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-user-circle me-1 text-warning"></i> ${escapeHtml(name)}
                </button>
                <ul class="dropdown-menu dropdown-menu-end shadow">
                    <li><a class="dropdown-item" href="/profile/"><i class="fa-solid fa-user me-2"></i> Profile</a></li>
                    <li><a class="dropdown-item" href="/my-borrowed/"><i class="fa-solid fa-book-bookmark me-2"></i> My Borrowed Books</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><button class="dropdown-item text-danger" onclick="logoutUserApp()"><i class="fa-solid fa-right-from-bracket me-2"></i> Logout</button></li>
                </ul>
            </div>
        `;
    } else {
        // Unauthenticated Navbar
        authWidget.innerHTML = `
            <a href="/login/" class="btn btn-login-outline me-2">Login</a>
            <a href="/signup/" class="btn btn-signup-solid">Signup</a>
        `;
    }
}

async function loadUserHomepage() {
    try {
        // Load Featured Books
        const resF = await fetchUserApi('/api/books/?featured=true');
        const dataF = await resF.json();
        const featured = dataF.results || (dataF.data ? dataF.data.results || dataF.data : []);
        renderBookCards('featured-books-container', featured);

        // Load Popular Books
        const resP = await fetchUserApi('/api/books/?popular=true');
        const dataP = await resP.json();
        const popular = dataP.results || (dataP.data ? dataP.data.results || dataP.data : []);
        renderBookCards('popular-books-container', popular);

        // Load Recently Added Books
        const resAll = await fetchUserApi('/api/books/?page=1');
        const dataAll = await resAll.json();
        const allBooks = dataAll.results || (dataAll.data ? dataAll.data.results || dataAll.data : []);
        renderBookCards('recently-added-container', allBooks.slice(0, 6));

        // Load Categories
        const resC = await fetchUserApi('/api/categories/');
        const dataC = await resC.json();
        const categories = dataC.data || dataC.results || [];
        renderCategoriesGrid('categories-grid-container', categories);
    } catch (err) {
        console.error('Error loading home data:', err);
    }
}

function renderBookCards(containerId, books) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (books.length === 0) {
        container.innerHTML = `<div class="col-12 text-center text-muted py-4">No books available in this section.</div>`;
        return;
    }

    container.innerHTML = books.map(b => `
        <div class="col-md-6 col-lg-4">
            <div class="card user-book-card h-100">
                <div class="book-cover-wrapper">
                    <img src="${b.cover_image_url || 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80'}" class="book-cover-img" alt="${escapeHtml(b.title)}">
                </div>
                <div class="card-body d-flex flex-column p-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="category-pill">${escapeHtml(b.category)}</span>
                        <div class="rating-stars">
                            <i class="fa-solid fa-star"></i> ${b.rating || '4.8'}
                        </div>
                    </div>
                    <h5 class="fw-bold text-dark mb-1 text-truncate">${escapeHtml(b.title)}</h5>
                    <p class="text-muted small mb-3"><i class="fa-solid fa-feather me-1"></i> ${escapeHtml(b.author_detail ? b.author_detail.name : 'Unknown Author')}</p>
                    
                    <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                        <span class="badge ${b.available_copies > 0 ? 'bg-success' : 'bg-danger'}">
                            ${b.available_copies > 0 ? `${b.available_copies} Available` : 'Out of Stock'}
                        </span>
                        <a href="/books/${b.id}/" class="btn btn-outline-primary btn-sm rounded-pill px-3">View Details</a>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function renderCategoriesGrid(containerId, categories) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (categories.length === 0) {
        container.innerHTML = `<div class="col-12 text-center text-muted">No categories loaded.</div>`;
        return;
    }

    container.innerHTML = categories.map(c => `
        <div class="col-md-3 col-6">
            <div class="card border-0 shadow-sm rounded-4 text-center p-3 hover-lift bg-white">
                <div class="rounded-circle bg-primary bg-opacity-10 text-primary mx-auto p-3 mb-2" style="width: 60px; height: 60px;">
                    <i class="fa-solid fa-layer-group fs-4"></i>
                </div>
                <h6 class="fw-bold mb-1">${escapeHtml(c.name)}</h6>
                <small class="text-muted">${c.books_count || 0} Books</small>
            </div>
        </div>
    `).join('');
}

async function borrowUserBook(bookId) {
    const token = getUserAccessToken();
    if (!token) {
        window.location.href = '/login/';
        return;
    }

    try {
        const res = await fetchUserApi('/api/borrow/', {
            method: 'POST',
            body: { book_id: bookId, days: 14 }
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showUserToast('Book borrowed successfully!', 'success');
            setTimeout(() => { window.location.href = '/my-borrowed/'; }, 600);
        } else {
            showUserToast(data.message || 'Borrow failed.', 'error');
        }
    } catch (e) {
        showUserToast('Error submitting borrow request.', 'error');
    }
}

async function returnUserBook(borrowId) {
    if (!confirm('Are you sure you want to return this book?')) return;

    try {
        const res = await fetchUserApi(`/api/borrow/${borrowId}/return/`, {
            method: 'POST'
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showUserToast('Book returned successfully!', 'success');
            setTimeout(() => { window.location.reload(); }, 600);
        } else {
            showUserToast(data.message || 'Return failed.', 'error');
        }
    } catch (e) {
        showUserToast('Error returning book.', 'error');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
}

document.addEventListener('DOMContentLoaded', setupUserNavbar);
