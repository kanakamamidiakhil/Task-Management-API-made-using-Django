from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    EmployeeCreateView, EmployeeListView, EmployeeDetailView, PromoteToAdminView,
    RegisterView, TaskViewSet
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Employee endpoints
    path('employees/create/', EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/promote/', PromoteToAdminView.as_view(), name='employee-promote'),

    # Register (set password)
    path('register/', RegisterView.as_view(), name='register'),

    # Task endpoints
    path('', include(router.urls)),
]
