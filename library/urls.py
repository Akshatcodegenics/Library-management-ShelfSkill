from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    AuthorViewSet,
    BookViewSet,
    MemberViewSet,
    BorrowView,
    ReturnView,
    BorrowHistoryView,
    OverdueView,
    DashboardView,
    FineViewSet,
    AuditLogViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register(r'members', MemberViewSet, basename='member')
router.register(r'fines', FineViewSet, basename='fine')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
    
    path('borrow/', BorrowView.as_view(), name='borrow-book'),
    path('borrow/<int:id>/return/', ReturnView.as_view(), name='return-book-id'),
    path('borrow/return/', ReturnView.as_view(), name='return-book'),
    path('borrow/overdue/', OverdueView.as_view(), name='borrow-overdue'),
    
    path('members/<int:id>/borrow-history/', BorrowHistoryView.as_view(), name='member-borrow-history'),
    path('members/me/borrow-history/', BorrowHistoryView.as_view(), name='my-borrow-history'),
    
    path('dashboard/', DashboardView.as_view(), name='dashboard-stats'),
]
