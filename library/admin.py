from django.contrib import admin
from .models import Author, Book, Member, BorrowRecord, Category, Fine, AuditLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'isbn', 'author', 'category', 'total_copies', 'available_copies', 'rating', 'is_featured', 'is_popular', 'created_at')
    list_filter = ('category', 'is_featured', 'is_popular', 'created_at')
    search_fields = ('title', 'isbn', 'category', 'author__name')
    ordering = ('-created_at',)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'membership_date', 'active_status')
    list_filter = ('active_status', 'membership_date')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-membership_date',)


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'member', 'borrowed_date', 'due_date', 'returned_date', 'status')
    list_filter = ('status', 'borrowed_date', 'due_date')
    search_fields = ('book__title', 'member__name', 'member__email')
    ordering = ('-borrowed_date',)


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'amount', 'paid_status', 'created_at')
    list_filter = ('paid_status', 'created_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'timestamp')
    search_fields = ('action', 'details', 'user__username')
