import django_filters
from django.db.models import Q
from .models import Book, Author


class BookFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search title, ISBN, category, author')
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')
    author = django_filters.ModelChoiceFilter(queryset=Author.objects.all())
    available = django_filters.BooleanFilter(method='filter_available', label='Available for borrow')
    featured = django_filters.BooleanFilter(field_name='is_featured')
    popular = django_filters.BooleanFilter(field_name='is_popular')

    class Meta:
        model = Book
        fields = ['search', 'category', 'author', 'available', 'featured', 'popular']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) |
            Q(isbn__icontains=value) |
            Q(category__icontains=value) |
            Q(author__name__icontains=value)
        )

    def filter_available(self, queryset, name, value):
        if value is True:
            return queryset.filter(available_copies__gt=0)
        elif value is False:
            return queryset.filter(available_copies=0)
        return queryset
