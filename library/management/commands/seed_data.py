from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from library.models import Author, Book, Member, BorrowRecord, BorrowStatus, Category, Fine, AuditLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds database with categories, authors, books (with covers/ratings), members, borrowing records, and admin account.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding Library System with separated User & Admin data...'))

        # 1. Admin Account
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'name': 'Library System Administrator'
            }
        )
        if created or not admin_user.check_password('adminpassword123'):
            admin_user.set_password('adminpassword123')
            admin_user.role = 'ADMIN'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created/Updated Admin User: admin / adminpassword123'))

        # 2. Demo User / Member Account
        member_user, created = User.objects.get_or_create(
            email='member@example.com',
            defaults={
                'username': 'demomember',
                'role': 'USER',
                'name': 'Jane Reader'
            }
        )
        if created:
            member_user.set_password('password123')
            member_user.save()
            Member.objects.create(
                user=member_user,
                name='Jane Reader',
                email='member@example.com',
                phone='+1 555 019 2831',
                active_status=True
            )
            self.stdout.write(self.style.SUCCESS('Created Demo User: member@example.com / password123'))

        member_profile = Member.objects.get(email='member@example.com')

        # 3. Categories
        categories_data = [
            ('Programming & Software', 'programming-software', 'Software development, architecture, algorithms, and code craftsmanship.'),
            ('Fiction & Literature', 'fiction-literature', 'Classics, modern novels, poetry, and storytelling.'),
            ('Data Science & AI', 'data-science-ai', 'Machine learning, artificial intelligence, data engineering, and analytics.'),
            ('Design & UX', 'design-ux', 'User experience design, graphic design, and interaction principles.')
        ]

        for name, slug, desc in categories_data:
            Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': desc})

        # 4. Authors
        authors_data = [
            ('Robert C. Martin', 'unclebob@example.com', 'Software engineer and author of Clean Code and Clean Architecture.'),
            ('Martin Fowler', 'fowler@example.com', 'Prominent software engineer, speaker, and author on software design.'),
            ('George Orwell', 'orwell@example.com', 'Classic novelist and essayist famous for 1984 and Animal Farm.'),
            ('Aurélien Géron', 'geron@example.com', 'Former YouTube ML engineer and author of Hands-On Machine Learning.')
        ]

        for name, email, bio in authors_data:
            user_inst, _ = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0], 'role': 'AUTHOR', 'name': name}
            )
            user_inst.set_password('password123')
            user_inst.save()
            Author.objects.get_or_create(
                email=email,
                defaults={'user': user_inst, 'name': name, 'biography': bio}
            )

        uncle_bob = Author.objects.get(email='unclebob@example.com')
        fowler = Author.objects.get(email='fowler@example.com')
        orwell = Author.objects.get(email='orwell@example.com')
        geron = Author.objects.get(email='geron@example.com')

        # 5. Books Dataset with Cover URLs & Ratings
        books_data = [
            {
                'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
                'isbn': '978-0132350884',
                'author': uncle_bob,
                'category': 'Programming & Software',
                'total_copies': 6,
                'available_copies': 4,
                'rating': Decimal('4.90'),
                'is_featured': True,
                'is_popular': True,
                'cover_image_url': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80'
            },
            {
                'title': 'Clean Architecture: A Craftsman\'s Guide to Software Structure',
                'isbn': '978-0134494166',
                'author': uncle_bob,
                'category': 'Programming & Software',
                'total_copies': 5,
                'available_copies': 5,
                'rating': Decimal('4.85'),
                'is_featured': True,
                'is_popular': False,
                'cover_image_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80'
            },
            {
                'title': 'Refactoring: Improving the Design of Existing Code',
                'isbn': '978-0201485677',
                'author': fowler,
                'category': 'Programming & Software',
                'total_copies': 4,
                'available_copies': 3,
                'rating': Decimal('4.80'),
                'is_featured': False,
                'is_popular': True,
                'cover_image_url': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80'
            },
            {
                'title': '1984 - Collector\'s Edition',
                'isbn': '978-0451524935',
                'author': orwell,
                'category': 'Fiction & Literature',
                'total_copies': 8,
                'available_copies': 7,
                'rating': Decimal('4.95'),
                'is_featured': True,
                'is_popular': True,
                'cover_image_url': 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80'
            },
            {
                'title': 'Animal Farm',
                'isbn': '978-0451526342',
                'author': orwell,
                'category': 'Fiction & Literature',
                'total_copies': 7,
                'available_copies': 7,
                'rating': Decimal('4.75'),
                'is_featured': False,
                'is_popular': False,
                'cover_image_url': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=600&q=80'
            },
            {
                'title': 'Hands-On Machine Learning with Scikit-Learn, Keras, & TensorFlow',
                'isbn': '978-1492032649',
                'author': geron,
                'category': 'Data Science & AI',
                'total_copies': 5,
                'available_copies': 4,
                'rating': Decimal('4.90'),
                'is_featured': True,
                'is_popular': True,
                'cover_image_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80'
            }
        ]

        for bdata in books_data:
            Book.objects.get_or_create(isbn=bdata['isbn'], defaults=bdata)

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(books_data)} books with high quality covers.'))

        # 6. Sample Borrow Records & Fines
        clean_code_book = Book.objects.get(isbn='978-0132350884')
        novel_1984 = Book.objects.get(isbn='978-0451524935')

        rec1, _ = BorrowRecord.objects.get_or_create(
            book=clean_code_book,
            member=member_profile,
            status=BorrowStatus.BORROWED,
            defaults={'due_date': timezone.now() + timedelta(days=10)}
        )

        rec2, _ = BorrowRecord.objects.get_or_create(
            book=novel_1984,
            member=member_profile,
            status=BorrowStatus.OVERDUE,
            defaults={'due_date': timezone.now() - timedelta(days=4)}
        )

        Fine.objects.get_or_create(
            borrow_record=rec2,
            defaults={'member': member_profile, 'amount': Decimal('4.00'), 'paid_status': False}
        )

        # 7. Audit Log Sample
        AuditLog.objects.get_or_create(
            action="SYSTEM_INIT",
            defaults={'user': admin_user, 'details': "System initialized with separated User Library App and Admin Panel."}
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded complete application dataset!'))
