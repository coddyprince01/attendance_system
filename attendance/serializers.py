from rest_framework import serializers
from .models import Lecturer, Student, Course, CourseEnrollment, Attendance, AttendanceToken
from django.contrib.auth.models import User

# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

# Lecturer serializer
class LecturerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    courses = serializers.StringRelatedField(many=True, read_only=True)
    # courses = CourseSerializer(many=True, read_only=True, source='courses')

    class Meta:
        model = Lecturer
        fields = ['id', 'user', 'name', 'profile_picture', 'courses']

# Course serializer must be defined before StudentSerializer
class CourseSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer()
    students = serializers.StringRelatedField(many=True, read_only=True)  # Simplified for clarity

    class Meta:
        model = Course
        fields = ['id', 'name', 'course_code', 'lecturer', 'students']

# Student serializer references CourseSerializer
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    courses = CourseSerializer(many=True, source='courses', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'name', 'courses']

# Course Enrollment serializer
class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = CourseEnrollment
        fields = ['student', 'enrolled_at']

# Attendance serializer
class AttendanceSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    present_students = StudentSerializer(many=True)
    missed_students = StudentSerializer(many=True)

    class Meta:
        model = Attendance
        fields = ['id', 'course', 'date', 'present_students', 'missed_students']

# Attendance token serializer
class AttendanceTokenSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = AttendanceToken
        fields = ['id', 'course', 'token', 'generated_at', 'expires_at']
