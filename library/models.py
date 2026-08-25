from django.db import models
from django.db.models import Q, F
from django.utils import timezone
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Author(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='author_profile'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    biography = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    isbn = models.CharField(max_length=20, unique=True, db_index=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.CharField(max_length=100, db_index=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image_url = models.CharField(max_length=500, blank=True, default='')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.50)
    is_featured = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['category']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(total_copies__gte=0),
                name='check_total_copies_gte_0'
            ),
            models.CheckConstraint(
                check=Q(available_copies__gte=0),
                name='check_available_copies_gte_0'
            ),
            models.CheckConstraint(
                check=Q(available_copies__lte=F('total_copies')),
                name='check_available_copies_lte_total'
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.available_copies > self.total_copies:
            raise ValidationError("Available copies cannot exceed total copies.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (ISBN: {self.isbn})"


class Member(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    membership_date = models.DateField(auto_now_add=True)
    active_status = models.BooleanField(default=True)

    class Meta:
        ordering = ['-membership_date']
        verbose_name = 'Member'
        verbose_name_plural = 'Members'

    def __str__(self):
        return f"{self.name} ({self.email})"


class BorrowStatus(models.TextChoices):
    BORROWED = 'BORROWED', 'Borrowed'
    RETURNED = 'RETURNED', 'Returned'
    OVERDUE = 'OVERDUE', 'Overdue'


class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='borrow_records')
    borrowed_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=BorrowStatus.choices,
        default=BorrowStatus.BORROWED,
        db_index=True
    )

    class Meta:
        ordering = ['-borrowed_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    @property
    def is_overdue(self) -> bool:
        if self.status == BorrowStatus.RETURNED:
            return False
        return self.due_date < timezone.now() and self.returned_date is None

    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        diff = timezone.now() - self.due_date
        return max(0, diff.days)

    def __str__(self):
        return f"Borrow #{self.id}: {self.book.title} by {self.member.name}"


class Fine(models.Model):
    borrow_record = models.OneToOneField(BorrowRecord, on_delete=models.CASCADE, related_name='fine')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='fines')
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    paid_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Fine ${self.amount} for {self.member.name} (Paid: {self.paid_status})"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.user}: {self.action}"
