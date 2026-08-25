from django.shortcuts import render, redirect
from django.views import View


# --------------------------------------------------------------------------
# ENTRANCE LANDING PAGE
# --------------------------------------------------------------------------

class EntranceLandingView(View):
    def get(self, request):
        return render(request, 'entrance_landing.html')


# --------------------------------------------------------------------------
# USER-FACING LIBRARY APP VIEWS
# --------------------------------------------------------------------------

class UserHomeView(View):
    def get(self, request):
        return render(request, 'user/home.html')


class UserShelfView(View):
    def get(self, request):
        return render(request, 'user/shelf.html')


class UserBooksView(View):
    def get(self, request):
        return render(request, 'user/books.html')


class UserBookDetailView(View):
    def get(self, request, id):
        return render(request, 'user/book-detail.html', {'book_id': id})


class UserLoginView(View):
    def get(self, request):
        return render(request, 'user/login.html')


class UserSignupView(View):
    def get(self, request):
        return render(request, 'user/signup.html')


class UserProfileView(View):
    def get(self, request):
        return render(request, 'user/profile.html')


class UserBorrowedView(View):
    def get(self, request):
        return render(request, 'user/borrowed.html')


class UserHistoryView(View):
    def get(self, request):
        return render(request, 'user/history.html')


# --------------------------------------------------------------------------
# SEPARATE ADMIN PANEL VIEWS
# --------------------------------------------------------------------------

class AdminLoginView(View):
    def get(self, request):
        return render(request, 'admin/login.html', {'hide_sidebar': True})


class AdminCreateAccountView(View):
    def get(self, request):
        return render(request, 'admin/create-account.html', {'hide_sidebar': True})


class AdminDashboardView(View):
    def get(self, request):
        return render(request, 'admin/dashboard.html')


class AdminBooksView(View):
    def get(self, request):
        return render(request, 'admin/books.html')


class AdminCategoriesView(View):
    def get(self, request):
        return render(request, 'admin/categories.html')


class AdminAuthorsView(View):
    def get(self, request):
        return render(request, 'admin/authors.html')


class AdminUsersView(View):
    def get(self, request):
        return render(request, 'admin/users.html')


class AdminBorrowingsView(View):
    def get(self, request):
        return render(request, 'admin/borrowings.html')


class AdminFinesView(View):
    def get(self, request):
        return render(request, 'admin/fines.html')


class AdminReportsView(View):
    def get(self, request):
        return render(request, 'admin/reports.html')


class AdminAuditLogsView(View):
    def get(self, request):
        return render(request, 'admin/audit_logs.html')


class AdminSettingsView(View):
    def get(self, request):
        return render(request, 'admin/settings.html')
