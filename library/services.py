from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from .models import Author, Book, Member, BorrowRecord, BorrowStatus, Fine, AuditLog

User = get_user_model()


class AuditService:
    @staticmethod
    def log(user, action: str, details: str = ''):
        try:
            AuditLog.objects.create(
                user=user if user and user.is_authenticated else None,
                action=action,
                details=details
            )
        except Exception:
            pass


class BorrowService:
    @staticmethod
    @transaction.atomic
    def borrow_book(user, book_id: int, days: int = 14) -> BorrowRecord:
        try:
            member = Member.objects.select_for_update().get(user=user)
        except Member.DoesNotExist:
            # Fallback: create member profile for normal user if missing
            member = Member.objects.create(
                user=user,
                name=user.name or user.username,
                email=user.email,
                phone="N/A",
                active_status=True
            )

        if not member.active_status:
            raise ValidationError({"error": "Member account is inactive. Borrowing privileges suspended."})

        try:
            book = Book.objects.select_for_update().get(pk=book_id)
        except Book.DoesNotExist:
            raise NotFound({"error": "Book not found."})

        if book.available_copies <= 0:
            raise ValidationError({"error": "No copies available for borrowing."})

        active_borrow_exists = BorrowRecord.objects.filter(
            member=member,
            book=book,
            status__in=[BorrowStatus.BORROWED, BorrowStatus.OVERDUE]
        ).exists()

        if active_borrow_exists:
            raise ValidationError({"error": "You have already borrowed this book."})

        book.available_copies -= 1
        book.save(update_fields=['available_copies'])

        due_date = timezone.now() + timedelta(days=days)
        borrow_record = BorrowRecord.objects.create(
            book=book,
            member=member,
            due_date=due_date,
            status=BorrowStatus.BORROWED
        )

        AuditService.log(user, "BOOK_BORROWED", f"Borrowed '{book.title}' (Borrow ID: {borrow_record.id})")
        return borrow_record


class ReturnService:
    @staticmethod
    @transaction.atomic
    def return_book(user, borrow_id: int) -> BorrowRecord:
        try:
            record = BorrowRecord.objects.select_for_update().get(pk=borrow_id)
        except BorrowRecord.DoesNotExist:
            raise NotFound({"error": "Borrow record not found."})

        is_admin = getattr(user, 'is_admin_user', False) or user.is_staff
        if not is_admin and record.member.user != user:
            raise PermissionDenied("You can only return books borrowed under your own member profile.")

        if record.status == BorrowStatus.RETURNED:
            raise ValidationError({"error": "This book has already been returned."})

        book = Book.objects.select_for_update().get(pk=record.book_id)
        if book.available_copies >= book.total_copies:
            book.available_copies = book.total_copies
        else:
            book.available_copies += 1
        book.save(update_fields=['available_copies'])

        record.returned_date = timezone.now()
        record.status = BorrowStatus.RETURNED
        record.save(update_fields=['returned_date', 'status'])

        # Automatic Fine calculation ($1.00 per day overdue)
        if record.due_date < record.returned_date:
            days_late = (record.returned_date - record.due_date).days
            if days_late > 0:
                amount = Decimal(days_late * 1.00)
                Fine.objects.get_or_create(
                    borrow_record=record,
                    defaults={'member': record.member, 'amount': amount, 'paid_status': False}
                )

        AuditService.log(user, "BOOK_RETURNED", f"Returned '{book.title}' (Borrow ID: {record.id})")
        return record


class OverdueService:
    @staticmethod
    def sync_and_get_overdue(user):
        now = timezone.now()
        expired_records = BorrowRecord.objects.filter(
            status=BorrowStatus.BORROWED,
            due_date__lt=now,
            returned_date__isnull=True
        )

        for rec in expired_records:
            rec.status = BorrowStatus.OVERDUE
            rec.save(update_fields=['status'])
            days_late = max(1, (now - rec.due_date).days)
            amount = Decimal(days_late * 1.00)
            Fine.objects.get_or_create(
                borrow_record=rec,
                defaults={'member': rec.member, 'amount': amount, 'paid_status': False}
            )

        qs = BorrowRecord.objects.filter(
            status=BorrowStatus.OVERDUE,
            returned_date__isnull=True
        ).select_related('book', 'book__author', 'member')

        is_admin = getattr(user, 'is_admin_user', False) or user.is_staff
        if is_admin:
            return qs
        elif getattr(user, 'is_author', False):
            return qs.filter(book__author__user=user)
        else:
            return qs.filter(member__user=user)


class DashboardService:
    @staticmethod
    def get_user_dashboard(user) -> dict:
        now = timezone.now()
        is_admin = getattr(user, 'is_admin_user', False) or user.is_staff

        if is_admin:
            total_books = Book.objects.count()
            available_books = Book.objects.filter(available_copies__gt=0).count()
            borrowed_books = BorrowRecord.objects.filter(status__in=[BorrowStatus.BORROWED, BorrowStatus.OVERDUE]).count()
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            overdue_books = BorrowRecord.objects.filter(status=BorrowStatus.OVERDUE).count()

            fines_agg = Fine.objects.aggregate(total=Sum('amount'))
            total_fines = float(fines_agg['total'] or 0.0)

            return {
                "role": "ADMIN",
                "total_books": total_books,
                "available_books": available_books,
                "borrowed_books": borrowed_books,
                "total_users": total_users,
                "active_users": active_users,
                "overdue_books": overdue_books,
                "total_fines": total_fines
            }
        elif getattr(user, 'is_author', False):
            author_profile = getattr(user, 'author_profile', None)
            author_books = Book.objects.filter(author=author_profile) if author_profile else Book.objects.filter(author__email=user.email)
            totals = author_books.aggregate(
                total_b=Count('id'),
                total_c=Sum('total_copies'),
                avail_c=Sum('available_copies')
            )
            total_books = totals['total_b'] or 0
            total_copies = totals['total_c'] or 0
            available_copies = totals['avail_c'] or 0
            borrowed_copies = max(0, total_copies - available_copies)

            return {
                "role": "AUTHOR",
                "total_books": total_books,
                "total_copies": total_copies,
                "available_copies": available_copies,
                "borrowed_copies": borrowed_copies,
                "active_borrowings": BorrowRecord.objects.filter(book__in=author_books, status__in=[BorrowStatus.BORROWED, BorrowStatus.OVERDUE]).count()
            }
        else:
            member_profile = getattr(user, 'member_profile', None)
            available_books = Book.objects.filter(available_copies__gt=0).count()
            
            if member_profile:
                member_records = BorrowRecord.objects.filter(member=member_profile)
                currently_borrowed = member_records.filter(status=BorrowStatus.BORROWED).count()
                overdue_books = member_records.filter(status=BorrowStatus.OVERDUE).count()
                total_borrowed = member_records.count()
            else:
                currently_borrowed = 0
                overdue_books = 0
                total_borrowed = 0

            return {
                "role": "USER",
                "available_books": available_books,
                "currently_borrowed": currently_borrowed,
                "overdue_books": overdue_books,
                "total_borrowed": total_borrowed
            }
