from rest_framework import serializers
from .models import Author, Book, Member, BorrowRecord, Category, Fine, AuditLog


class CategorySerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'books_count', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_books_count(self, obj) -> int:
        return Book.objects.filter(category__iexact=obj.name).count()


class AuthorSerializer(serializers.ModelSerializer):
    books_count = serializers.IntegerField(source='books.count', read_only=True)

    class Meta:
        model = Author
        fields = ('id', 'name', 'email', 'biography', 'books_count', 'created_at')
        read_only_fields = ('id', 'created_at')


class BookAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name', 'email')


class BookSerializer(serializers.ModelSerializer):
    author_detail = BookAuthorSerializer(source='author', read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source='author',
        write_only=True,
        required=False
    )
    borrowed_copies = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'isbn', 'category', 'total_copies',
            'available_copies', 'borrowed_copies', 'cover_image_url',
            'rating', 'is_featured', 'is_popular', 'author', 'author_id',
            'author_detail', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'available_copies')
        extra_kwargs = {
            'author': {'required': False}
        }

    def get_borrowed_copies(self, obj) -> int:
        return max(0, obj.total_copies - obj.available_copies)

    def validate_isbn(self, value):
        isbn = value.strip()
        qs = Book.objects.filter(isbn__iexact=isbn)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A book with this ISBN already exists.")
        return isbn

    def validate_total_copies(self, value):
        if value < 0:
            raise serializers.ValidationError("Total copies must be greater than or equal to 0.")
        return value

    def validate(self, attrs):
        total_copies = attrs.get('total_copies', getattr(self.instance, 'total_copies', 1))
        
        if not self.instance:
            attrs['available_copies'] = total_copies
        else:
            current_borrowed = self.instance.total_copies - self.instance.available_copies
            if total_copies < current_borrowed:
                raise serializers.ValidationError({
                    "total_copies": f"Cannot set total_copies to {total_copies} because {current_borrowed} copies are currently borrowed."
                })
            attrs['available_copies'] = total_copies - current_borrowed

        return attrs


class MemberSerializer(serializers.ModelSerializer):
    currently_borrowed_count = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ('id', 'user', 'name', 'email', 'phone', 'membership_date', 'active_status', 'currently_borrowed_count')
        read_only_fields = ('id', 'membership_date', 'user')

    def get_currently_borrowed_count(self, obj) -> int:
        return obj.borrow_records.filter(status__in=['BORROWED', 'OVERDUE']).count()


class BorrowRecordSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    member = MemberSerializer(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)

    class Meta:
        model = BorrowRecord
        fields = (
            'id', 'book', 'member', 'borrowed_date',
            'due_date', 'returned_date', 'status', 'days_overdue'
        )
        read_only_fields = fields


class FineSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)
    member_email = serializers.CharField(source='member.email', read_only=True)
    book_title = serializers.CharField(source='borrow_record.book.title', read_only=True)

    class Meta:
        model = Fine
        fields = ('id', 'borrow_record', 'member', 'member_name', 'member_email', 'book_title', 'amount', 'paid_status', 'created_at')
        read_only_fields = ('id', 'created_at')


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'username', 'action', 'details', 'timestamp')
        read_only_fields = ('id', 'timestamp')


class BorrowRequestSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(required=True)
    days = serializers.IntegerField(default=14, min_value=1, max_value=60)


class ReturnRequestSerializer(serializers.Serializer):
    borrow_id = serializers.IntegerField(required=False)
