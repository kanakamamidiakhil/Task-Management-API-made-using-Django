from rest_framework import serializers
from .models import Employee, Task, TaskEditLog

class EmployeeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'phone', 'role', 'date_joined']
        read_only_fields = ['role', 'date_joined']

class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone']
    def create(self, validated_data):
        # password not set here; registration endpoint will set password.
        return Employee.objects.create(**validated_data)

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        try:
            user = Employee.objects.get(email=data['email'])
        except Employee.DoesNotExist:
            raise serializers.ValidationError("No employee found with this email. Contact admin.")
        return data

    def save(self, **kwargs):
        email = self.validated_data['email']
        password = self.validated_data['password']
        user = Employee.objects.get(email=email)
        user.set_password(password)
        user.save()
        return user

class TaskSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'employee', 'description', 'status', 'created_at', 'updated_at']

class TaskEditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskEditLog
        fields = ['id', 'task', 'edited_by', 'old_description', 'old_status', 'edited_at']
