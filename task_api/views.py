from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Employee, Task, TaskEditLog
from .serializers import (
    EmployeeSerializer, EmployeeCreateSerializer, RegisterSerializer,
    TaskSerializer, TaskEditLogSerializer
)
from .permissions import IsSuperAdmin, IsAdminOrSuper

# Create employee (admin and superadmin can create employees)
class EmployeeCreateView(generics.CreateAPIView):
    serializer_class = EmployeeCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuper]

# List all employees (authenticated users can view)
class EmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer

# Retrieve / Update / Delete employee
class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # For update/delete operations, only admin or superadmin permitted, with some restrictions
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminOrSuper()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        employee = self.get_object()
        # id not editable, role change only allowed via promote endpoint
        data = request.data.copy()
        for forbidden in ['id', 'role']:
            if forbidden in data:
                data.pop(forbidden)
        serializer = self.get_serializer(employee, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Prevent admin from editing admins/superadmin
        if request.user.role == 'admin' and employee.role != 'employee':
            return Response({'detail': 'Admin can only edit employees (not admins or superadmin).'}, status=403)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        employee = self.get_object()
        if employee.role == 'superadmin':
            return Response({'detail': 'Superadmin cannot be deleted.'}, status=403)
        # Admins cannot delete admins or superadmin
        if request.user.role == 'admin' and employee.role != 'employee':
            return Response({'detail': 'Admin can only delete employees (not admins or superadmin).'}, status=403)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Promote employee to admin (superadmin only)
from rest_framework.views import APIView

class PromoteToAdminView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        if employee.role == 'superadmin':
            return Response({'detail': 'Cannot change role of superadmin.'}, status=400)
        employee.role = 'admin'
        employee.save()
        return Response({'detail': f'Employee {employee.email} promoted to admin.'})

# Registration endpoint: set password for existing employee via email
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

# TASK VIEWS
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuper]
    filter_backends = [filters.SearchFilter]
    search_fields = ['status']

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_update(self, serializer):
        # log changes
        task = self.get_object()
        old_description = task.description
        old_status = task.status
        editor = self.request.user
        serializer.save()
        TaskEditLog.objects.create(
            task=task,
            edited_by=editor,
            old_description=old_description,
            old_status=old_status
        )
