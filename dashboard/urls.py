from django.urls import path
from .views import (
    EntranceLandingView,
    UserHomeView,
    UserShelfView,
    UserBooksView,
    UserBookDetailView,
    UserLoginView,
    UserSignupView,
    UserProfileView,
    UserBorrowedView,
    UserHistoryView,
    AdminLoginView,
    AdminCreateAccountView,
    AdminDashboardView,
    AdminBooksView,
    AdminCategoriesView,
    AdminAuthorsView,
    AdminUsersView,
    AdminBorrowingsView,
    AdminFinesView,
    AdminReportsView,
    AdminAuditLogsView,
    AdminSettingsView
)

urlpatterns = [
    # ----------------------------------------------------------------------
    # ENTRANCE LANDING PAGE
    # ----------------------------------------------------------------------
    path('', EntranceLandingView.as_view(), name='entrance-landing'),

    # ----------------------------------------------------------------------
    # USER-FACING LIBRARY APP ROUTES
    # ----------------------------------------------------------------------
    path('home/', UserHomeView.as_view(), name='user-home'),
    path('shelf/', UserShelfView.as_view(), name='user-shelf'),
    path('books/', UserBooksView.as_view(), name='user-books'),
    path('books/<int:id>/', UserBookDetailView.as_view(), name='user-book-detail'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    path('register/', UserSignupView.as_view(), name='user-register-alias'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('my-borrowed/', UserBorrowedView.as_view(), name='user-borrowed'),
    path('history/', UserHistoryView.as_view(), name='user-history'),

    # ----------------------------------------------------------------------
    # DEDICATED SEPARATE ADMIN PANEL ROUTES
    # ----------------------------------------------------------------------
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('admin/create-account/', AdminCreateAccountView.as_view(), name='admin-create-account'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/books/', AdminBooksView.as_view(), name='admin-books'),
    path('admin/categories/', AdminCategoriesView.as_view(), name='admin-categories'),
    path('admin/authors/', AdminAuthorsView.as_view(), name='admin-authors'),
    path('admin/users/', AdminUsersView.as_view(), name='admin-users'),
    path('admin/borrowings/', AdminBorrowingsView.as_view(), name='admin-borrowings'),
    path('admin/fines/', AdminFinesView.as_view(), name='admin-fines'),
    path('admin/reports/', AdminReportsView.as_view(), name='admin-reports'),
    path('admin/audit-logs/', AdminAuditLogsView.as_view(), name='admin-audit-logs'),
    path('admin/settings/', AdminSettingsView.as_view(), name='admin-settings'),
]
