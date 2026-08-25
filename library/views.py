from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Author, Book, Member, BorrowRecord, Category, Fine, AuditLog
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    MemberSerializer,
    BorrowRecordSerializer,
    BorrowRequestSerializer,
    ReturnRequestSerializer,
    CategorySerializer,
    FineSerializer,
    AuditLogSerializer
)
from .filters import BookFilter
from .permissions import (
    IsAdminUserOrReadOnly,
    IsBookOwnerAuthorOrReadOnly,
    IsMemberSelfOrAdmin
)
from accounts.permissions import IsAdminUserRole, IsMember
from .services import BorrowService, ReturnService, OverdueService, DashboardService, AuditService


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminUserOrReadOnly]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Categories retrieved.",
            "data": response.data
        })


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOrReadOnly]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Authors retrieved successfully.",
            "data": response.data
        })

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Author retrieved successfully.",
            "data": response.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            author = serializer.save()
            AuditService.log(request.user, "AUTHOR_CREATED", f"Created author: {author.name}")
            return Response({
                "success": True,
                "message": "Author created successfully.",
                "data": AuthorSerializer(author).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsBookOwnerAuthorOrReadOnly]
    filterset_class = BookFilter
    search_fields = ['title', 'isbn', 'category', 'author__name']
    ordering_fields = ['title', 'created_at', 'available_copies', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'author_profile') and not self.request.data.get('author'):
            book = serializer.save(author=self.request.user.author_profile)
        else:
            # If no author specified, attach to first default author or system admin
            if not self.request.data.get('author') and Author.objects.exists():
                book = serializer.save(author=Author.objects.first())
            else:
                book = serializer.save()
        AuditService.log(self.request.user, "BOOK_CREATED", f"Published book: {book.title}")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Books retrieved successfully.",
            "data": response.data
        })

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Book details retrieved successfully.",
            "data": response.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "success": True,
                "message": "Book created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            AuditService.log(request.user, "BOOK_UPDATED", f"Updated book ID: {instance.id}")
            return Response({
                "success": True,
                "message": "Book updated successfully.",
                "data": serializer.data
            })
        return Response({
            "success": False,
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.title
        self.perform_destroy(instance)
        AuditService.log(request.user, "BOOK_DELETED", f"Deleted book: {title}")
        return Response({
            "success": True,
            "message": "Book deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all().select_related('user')
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsMemberSelfOrAdmin]

    def list(self, request, *args, **kwargs):
        if not getattr(request.user, 'is_admin_user', False) and not request.user.is_staff:
            qs = self.queryset.filter(user=request.user)
        else:
            qs = self.queryset
        serializer = self.get_serializer(qs, many=True)
        return Response({
            "success": True,
            "message": "Members retrieved successfully.",
            "data": serializer.data
        })


class BorrowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=BorrowRequestSerializer)
    def post(self, request):
        serializer = BorrowRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        book_id = serializer.validated_data['book_id']
        days = serializer.validated_data.get('days', 14)

        try:
            record = BorrowService.borrow_book(request.user, book_id=book_id, days=days)
            return Response({
                "success": True,
                "message": "Book borrowed successfully.",
                "data": BorrowRecordSerializer(record).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            err_data = getattr(e, 'detail', str(e))
            msg = err_data.get('error', str(err_data)) if isinstance(err_data, dict) else str(err_data)
            return Response({
                "success": False,
                "message": msg,
                "errors": err_data
            }, status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST))


class ReturnView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ReturnRequestSerializer)
    def post(self, request, id=None):
        borrow_id = id or request.data.get('borrow_id')
        if not borrow_id:
            return Response({
                "success": False,
                "message": "Borrow ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            record = ReturnService.return_book(request.user, borrow_id=int(borrow_id))
            return Response({
                "success": True,
                "message": "Book returned successfully.",
                "data": BorrowRecordSerializer(record).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            err_data = getattr(e, 'detail', str(e))
            msg = err_data.get('error', str(err_data)) if isinstance(err_data, dict) else str(err_data)
            return Response({
                "success": False,
                "message": msg,
                "errors": err_data
            }, status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST))


class BorrowHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        if id:
            try:
                member = Member.objects.get(pk=id)
            except Member.DoesNotExist:
                return Response({"success": False, "message": "Member not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                member = Member.objects.get(user=request.user)
            except Member.DoesNotExist:
                return Response({"success": False, "message": "Member profile not found."}, status=status.HTTP_404_NOT_FOUND)

        is_admin = getattr(request.user, 'is_admin_user', False) or request.user.is_staff
        if not is_admin and member.user != request.user:
            return Response({"success": False, "message": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        qs = BorrowRecord.objects.filter(member=member).select_related('book', 'book__author')
        serializer = BorrowRecordSerializer(qs, many=True)
        return Response({
            "success": True,
            "message": "Borrow history retrieved.",
            "data": serializer.data
        })


class OverdueView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = OverdueService.sync_and_get_overdue(request.user)
        serializer = BorrowRecordSerializer(qs, many=True)
        return Response({
            "success": True,
            "message": "Overdue records retrieved successfully.",
            "data": serializer.data
        })


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stats = DashboardService.get_user_dashboard(request.user)
        return Response({
            "success": True,
            "message": "Dashboard statistics retrieved.",
            "data": stats
        })


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all().select_related('member', 'borrow_record', 'borrow_record__book')
    serializer_class = FineSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Fines retrieved.",
            "data": response.data
        })


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().select_related('user')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Audit logs retrieved.",
            "data": response.data
        })
