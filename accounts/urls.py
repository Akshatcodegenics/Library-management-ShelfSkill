from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserSignupView,
    AdminRegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    MeView,
    UserAdminViewSet
)

router = DefaultRouter()
router.register(r'users', UserAdminViewSet, basename='admin-user-manage')

urlpatterns = [
    path('register/', UserSignupView.as_view(), name='auth-register-compat'),
    path('signup/', UserSignupView.as_view(), name='auth-signup'),
    path('admin/register/', AdminRegisterView.as_view(), name='auth-admin-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('', include(router.urls)),
]
