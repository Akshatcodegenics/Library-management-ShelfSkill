// Author Portal Frontend Controller

async function loadAuthorDashboard() {
    try {
        const res = await fetchWithAuth('/api/dashboard/');
        const data = await res.json();
        if (res.ok && data.success) {
            const stats = data.data;
            document.getElementById('card-total-books').textContent = stats.total_books || 0;
            document.getElementById('card-total-copies').textContent = stats.total_copies || 0;
            document.getElementById('card-available-copies').textContent = stats.available_copies || 0;
            document.getElementById('card-borrowed-copies').textContent = stats.borrowed_copies || 0;
        }
        loadAuthorBooksTablePreview();
    } catch (err) {
        console.error('Error loading dashboard:', err);
    }
}

async function loadAuthorBooksTablePreview() {
    const tbody = document.getElementById('books-table-body');
    if (!tbody) return;

    try {
        const res = await fetchWithAuth('/api/books/');
        const data = await res.json();
        const books = data.results || (data.data ? data.data.results || data.data : []);

        if (books.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No books created yet. <a href="/author/books/create/">Add your first book</a></td></tr>`;
            return;
        }

        tbody.innerHTML = books.slice(0, 5).map(b => `
            <tr>
                <td class="fw-bold">${escapeHtml(b.title)}</td>
                <td><code>${escapeHtml(b.isbn)}</code></td>
                <td><span class="badge bg-secondary">${escapeHtml(b.category)}</span></td>
                <td>${b.total_copies}</td>
                <td><span class="badge bg-success">${b.available_copies}</span></td>
                <td><span class="badge bg-warning text-dark">${b.borrowed_copies}</span></td>
                <td>
                    <a href="/author/books/${b.id}/edit/" class="btn btn-sm btn-outline-primary me-1"><i class="fa-solid fa-pen"></i> Edit</a>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteAuthorBook(${b.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">Failed to load books.</td></tr>`;
    }
}

async function loadAuthorBooksList() {
    const tbody = document.getElementById('full-books-body');
    if (!tbody) return;

    try {
        const res = await fetchWithAuth('/api/books/');
        const data = await res.json();
        const books = data.results || (data.data ? data.data.results || data.data : []);

        if (books.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No books published. <a href="/author/books/create/">Publish a book now</a></td></tr>`;
            return;
        }

        tbody.innerHTML = books.map(b => `
            <tr>
                <td class="fw-bold">${escapeHtml(b.title)}</td>
                <td><code>${escapeHtml(b.isbn)}</code></td>
                <td><span class="badge bg-secondary">${escapeHtml(b.category)}</span></td>
                <td>${b.total_copies}</td>
                <td><span class="badge bg-success">${b.available_copies}</span></td>
                <td><span class="badge bg-warning text-dark">${b.borrowed_copies}</span></td>
                <td class="text-end pe-4">
                    <a href="/author/books/${b.id}/edit/" class="btn btn-sm btn-outline-primary me-1"><i class="fa-solid fa-pen me-1"></i>Edit</a>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteAuthorBook(${b.id})"><i class="fa-solid fa-trash me-1"></i>Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">Failed to load books list.</td></tr>`;
    }
}

async function initBookForm(mode, bookId) {
    const form = document.getElementById('book-form');
    if (!form) return;

    if (mode === 'edit' && bookId) {
        try {
            const res = await fetchWithAuth(`/api/books/${bookId}/`);
            const data = await res.json();
            if (res.ok && data.success) {
                const book = data.data;
                document.getElementById('book-title').value = book.title;
                document.getElementById('book-isbn').value = book.isbn;
                document.getElementById('book-category').value = book.category;
                document.getElementById('book-copies').value = book.total_copies;
            }
        } catch (e) {
            showToast('Failed to load book data for editing.', 'error');
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const alertBox = document.getElementById('form-alert');
        const spinner = document.getElementById('save-spinner');
        const btn = document.getElementById('save-book-btn');

        alertBox.classList.add('d-none');
        spinner.classList.remove('d-none');
        btn.disabled = true;

        const payload = {
            title: document.getElementById('book-title').value.trim(),
            isbn: document.getElementById('book-isbn').value.trim(),
            category: document.getElementById('book-category').value.trim(),
            total_copies: parseInt(document.getElementById('book-copies').value)
        };

        const url = mode === 'edit' ? `/api/books/${bookId}/` : '/api/books/';
        const method = mode === 'edit' ? 'PUT' : 'POST';

        try {
            const res = await fetchWithAuth(url, { method, body: payload });
            const data = await res.json();

            if (res.ok && data.success) {
                showToast(`Book ${mode === 'edit' ? 'updated' : 'published'} successfully!`, 'success');
                setTimeout(() => { window.location.href = '/author/books/'; }, 500);
            } else {
                let msg = data.message || 'Operation failed.';
                if (data.errors) {
                    const errs = Object.entries(data.errors).map(([k, v]) => `${k}: ${v}`).join('<br>');
                    msg += `<br><small>${errs}</small>`;
                }
                alertBox.innerHTML = msg;
                alertBox.classList.remove('d-none');
            }
        } catch (err) {
            alertBox.textContent = 'Server communication error.';
            alertBox.classList.remove('d-none');
        } finally {
            spinner.classList.add('d-none');
            btn.disabled = false;
        }
    });
}

async function deleteAuthorBook(bookId) {
    if (!confirm('Are you sure you want to delete this book?')) return;

    try {
        const res = await fetchWithAuth(`/api/books/${bookId}/`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Book deleted successfully.', 'success');
            loadAuthorBooksList();
            loadAuthorDashboard();
        } else {
            const data = await res.json();
            showToast(data.message || 'Failed to delete book.', 'error');
        }
    } catch (e) {
        showToast('Error deleting book.', 'error');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
}
