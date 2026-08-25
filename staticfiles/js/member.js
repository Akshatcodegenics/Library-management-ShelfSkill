// Member Portal Frontend Controller

let currentPage = 1;
let currentSearch = '';
let currentCategory = '';
let currentAvailability = '';

async function loadMemberDashboard() {
    try {
        const res = await fetchWithAuth('/api/dashboard/');
        const data = await res.json();
        if (res.ok && data.success) {
            const stats = data.data;
            document.getElementById('card-available-books').textContent = stats.available_books || 0;
            document.getElementById('card-currently-borrowed').textContent = stats.currently_borrowed || 0;
            document.getElementById('card-overdue-books').textContent = stats.overdue_books || 0;
            document.getElementById('card-total-borrowed').textContent = stats.total_borrowed || 0;
        }
        loadMemberActiveLoansPreview();
    } catch (err) {
        console.error('Error loading member dashboard:', err);
    }
}

async function loadMemberActiveLoansPreview() {
    const tbody = document.getElementById('member-active-loans-body');
    if (!tbody) return;

    try {
        const res = await fetchWithAuth('/api/members/me/borrow-history/');
        const data = await res.json();
        const records = data.results || (data.data ? data.data.results || data.data : []);
        const active = records.filter(r => r.status === 'BORROWED' || r.status === 'OVERDUE');

        if (active.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No active loans. <a href="/member/books/">Browse library catalogue</a></td></tr>`;
            return;
        }

        tbody.innerHTML = active.slice(0, 5).map(r => `
            <tr>
                <td class="fw-bold">${escapeHtml(r.book.title)}</td>
                <td>${formatDate(r.borrowed_date)}</td>
                <td>${formatDate(r.due_date)}</td>
                <td><span class="badge ${r.status === 'OVERDUE' ? 'badge-status-overdue' : 'badge-status-borrowed'}">${r.status}</span></td>
                <td class="text-end pe-3">
                    <button class="btn btn-sm btn-outline-success" onclick="returnBookAction(${r.id})">Return</button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">Failed to load active loans.</td></tr>`;
    }
}

async function initBrowseBooks() {
    const filterForm = document.getElementById('filter-form');
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');

    if (filterForm) {
        filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            currentSearch = document.getElementById('search-input').value.trim();
            currentCategory = document.getElementById('category-filter').value;
            currentAvailability = document.getElementById('availability-filter').value;
            currentPage = 1;
            fetchBooksCatalogue();
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                fetchBooksCatalogue();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentPage++;
            fetchBooksCatalogue();
        });
    }

    fetchBooksCatalogue();
}

async function fetchBooksCatalogue() {
    const container = document.getElementById('books-cards-container');
    if (!container) return;

    let url = `/api/books/?page=${currentPage}`;
    if (currentSearch) url += `&search=${encodeURIComponent(currentSearch)}`;
    if (currentCategory) url += `&category=${encodeURIComponent(currentCategory)}`;
    if (currentAvailability) url += `&available=${encodeURIComponent(currentAvailability)}`;

    container.innerHTML = `<div class="col-12 text-center py-5 text-muted"><div class="spinner-border text-primary"></div><p class="mt-2">Loading books...</p></div>`;

    try {
        const res = await fetchWithAuth(url);
        const data = await res.json();
        const results = data.results || (data.data ? data.data.results || data.data : []);
        const count = data.count || (data.data ? data.data.count : results.length);

        updatePagination(count, !!data.next, !!data.previous);

        if (results.length === 0) {
            container.innerHTML = `<div class="col-12 text-center py-5 text-muted"><h5>No books match your criteria.</h5><p>Try clearing filters or search term.</p></div>`;
            return;
        }

        container.innerHTML = results.map(b => `
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 border-0 shadow-sm rounded-3 book-card">
                    <div class="card-body d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-secondary">${escapeHtml(b.category)}</span>
                            <span class="badge ${b.available_copies > 0 ? 'bg-success' : 'bg-danger'}">
                                ${b.available_copies > 0 ? `${b.available_copies} Available` : 'Unavailable'}
                            </span>
                        </div>
                        <h5 class="card-title fw-bold text-dark mb-1">${escapeHtml(b.title)}</h5>
                        <p class="text-muted small mb-2"><i class="fa-solid fa-feather me-1"></i> ${escapeHtml(b.author_detail ? b.author_detail.name : 'Unknown Author')}</p>
                        <small class="text-secondary d-block mb-3">ISBN: <code>${escapeHtml(b.isbn)}</code></small>
                        
                        <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                            <a href="/member/books/${b.id}/" class="btn btn-outline-primary btn-sm">
                                <i class="fa-solid fa-circle-info me-1"></i> Details
                            </a>
                            ${b.available_copies > 0 ? `
                                <button class="btn btn-primary btn-sm fw-bold" onclick="borrowBookAction(${b.id})">
                                    <i class="fa-solid fa-bookmark me-1"></i> Borrow
                                </button>
                            ` : `
                                <button class="btn btn-secondary btn-sm" disabled>Unavailable</button>
                            `}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = `<div class="col-12 text-center text-danger py-5">Error loading catalogue.</div>`;
    }
}

function updatePagination(count, hasNext, hasPrev) {
    const info = document.getElementById('pagination-info');
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');

    if (info) info.textContent = `Page ${currentPage} (Total ${count} items)`;
    if (prevBtn) prevBtn.disabled = !hasPrev && currentPage === 1;
    if (nextBtn) nextBtn.disabled = !hasNext;
}

async function loadBookDetail(bookId) {
    const container = document.getElementById('book-detail-container');
    if (!container) return;

    try {
        const res = await fetchWithAuth(`/api/books/${bookId}/`);
        const data = await res.json();
        if (res.ok && data.success) {
            const b = data.data;
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-8">
                        <span class="badge bg-secondary mb-2">${escapeHtml(b.category)}</span>
                        <h2 class="fw-bold mb-2">${escapeHtml(b.title)}</h2>
                        <h5 class="text-primary mb-3">Author: ${escapeHtml(b.author_detail ? b.author_detail.name : 'Unknown')}</h5>
                        <p class="text-muted">${escapeHtml(b.author_detail ? b.author_detail.biography || 'No biography provided.' : '')}</p>
                    </div>
                    <div class="col-md-4 border-start">
                        <div class="p-3 bg-light rounded">
                            <small class="text-muted d-block fw-semibold mb-1">ISBN Number</small>
                            <code class="fs-6 text-dark">${escapeHtml(b.isbn)}</code>
                            
                            <hr>

                            <small class="text-muted d-block fw-semibold mb-1">Total Copies</small>
                            <p class="fw-bold text-dark mb-2">${b.total_copies}</p>

                            <small class="text-muted d-block fw-semibold mb-1">Available Copies</small>
                            <p class="fw-bold ${b.available_copies > 0 ? 'text-success' : 'text-danger'} fs-5 mb-3">${b.available_copies}</p>

                            ${b.available_copies > 0 ? `
                                <button class="btn btn-primary w-100 fw-bold py-2 shadow-sm" onclick="borrowBookAction(${b.id})">
                                    <i class="fa-solid fa-bookmark me-1"></i> Borrow Book Now
                                </button>
                            ` : `
                                <div class="alert alert-warning text-center mb-0">Currently Unavailable</div>
                            `}
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = `<div class="text-center text-danger py-4">Failed to load book details.</div>`;
    }
}

async function borrowBookAction(bookId) {
    try {
        const res = await fetchWithAuth('/api/borrow/', {
            method: 'POST',
            body: { book_id: bookId, days: 14 }
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast('Book borrowed successfully! Due in 14 days.', 'success');
            setTimeout(() => { window.location.href = '/member/borrowed/'; }, 600);
        } else {
            showToast(data.message || 'Failed to borrow book.', 'error');
        }
    } catch (e) {
        showToast('Error issuing borrow request.', 'error');
    }
}

async function returnBookAction(borrowId) {
    if (!confirm('Are you sure you want to return this book?')) return;

    try {
        const res = await fetchWithAuth(`/api/borrow/${borrowId}/return/`, {
            method: 'POST'
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast('Book returned successfully!', 'success');
            if (window.location.pathname.includes('borrowed')) {
                loadBorrowedBooksList();
            } else if (window.location.pathname.includes('overdue')) {
                loadOverdueBooks();
            } else {
                loadMemberDashboard();
            }
        } else {
            showToast(data.message || 'Failed to return book.', 'error');
        }
    } catch (e) {
        showToast('Error returning book.', 'error');
    }
}

async function loadBorrowedBooksList() {
    const tbody = document.getElementById('borrowed-books-list');
    if (!tbody) return;

    try {
        const res = await fetchWithAuth('/api/members/me/borrow-history/');
        const data = await res.json();
        const records = data.results || (data.data ? data.data.results || data.data : []);
        const active = records.filter(r => r.status === 'BORROWED' || r.status === 'OVERDUE');

        if (active.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">You have no active borrowed books. <a href="/member/books/">Browse catalogue</a></td></tr>`;
            return;
        }

        tbody.innerHTML = active.map(r => `
            <tr>
                <td class="fw-bold">${escapeHtml(r.book.title)}</td>
                <td>${escapeHtml(r.book.author_detail ? r.book.author_detail.name : 'Unknown')}</td>
                <td><span class="badge bg-secondary">${escapeHtml(r.book.category)}</span></td>
                <td>${formatDate(r.borrowed_date)}</td>
                <td>${formatDate(r.due_date)}</td>
                <td><span class="badge ${r.status === 'OVERDUE' ? 'badge-status-overdue' : 'badge-status-borrowed'}">${r.status}</span></td>
                <td class="text-end pe-4">
                    <button class="btn btn-sm btn-success fw-bold" onclick="returnBookAction(${r.id})">Return Book</button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">Failed to load borrowed books.</td></tr>`;
    }
}

async function loadBorrowingHistory() {
    const tbody = document.getElementById('history-table-body');
    if (!tbody) return;

    try {
        const res = await fetchWithAuth('/api/members/me/borrow-history/');
        const data = await res.json();
        const records = data.results || (data.data ? data.data.results || data.data : []);

        if (records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No borrowing history recorded yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = records.map(r => `
            <tr>
                <td class="fw-bold">${escapeHtml(r.book.title)}</td>
                <td>${escapeHtml(r.book.author_detail ? r.book.author_detail.name : 'Unknown')}</td>
                <td>${formatDate(r.borrowed_date)}</td>
                <td>${formatDate(r.due_date)}</td>
                <td>${r.returned_date ? formatDate(r.returned_date) : '<span class="text-muted">Not Returned</span>'}</td>
                <td><span class="badge ${r.status === 'RETURNED' ? 'badge-status-returned' : (r.status === 'OVERDUE' ? 'badge-status-overdue' : 'badge-status-borrowed')}">${r.status}</span></td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">Failed to load history.</td></tr>`;
    }
}

async function loadOverdueBooks() {
    const tbody = document.getElementById('overdue-table-body');
    if (!tbody) return;

    try {
        const res = await fetchWithAuth('/api/borrow/overdue/');
        const data = await res.json();
        const records = data.data || [];

        if (records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-success fw-bold"><i class="fa-solid fa-circle-check me-2"></i>No overdue books! All your active loans are on schedule.</td></tr>`;
            return;
        }

        tbody.innerHTML = records.map(r => `
            <tr>
                <td class="fw-bold">${escapeHtml(r.book.title)}</td>
                <td>${escapeHtml(r.book.author_detail ? r.book.author_detail.name : 'Unknown')}</td>
                <td>${formatDate(r.borrowed_date)}</td>
                <td class="text-danger fw-bold">${formatDate(r.due_date)}</td>
                <td><span class="badge bg-danger fs-6">${r.days_overdue} days</span></td>
                <td><span class="badge badge-status-overdue">OVERDUE</span></td>
                <td class="text-end pe-4">
                    <button class="btn btn-sm btn-success fw-bold" onclick="returnBookAction(${r.id})">Return Immediately</button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">Failed to load overdue books.</td></tr>`;
    }
}

function formatDate(isoString) {
    if (!isoString) return 'N/A';
    const d = new Date(isoString);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
}
