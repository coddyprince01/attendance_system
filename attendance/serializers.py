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
    user = UserSerializer(read_only=True)
    courses = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Refers to related courses

    class Meta:
        model = Lecturer
        fields = ['id', 'user', 'staff_id', 'name', 'profile_picture', 'courses']


# Course serializer
class CourseSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer(read_only=True)
    students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Refers to related students

    class Meta:
        model = Course
        fields = ['id', 'name', 'course_code', 'lecturer', 'students']


# Student serializer
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    courses = CourseSerializer(many=True, read_only=True)  # Refers to related courses

    class Meta:
        model = Student
        fields = ['id', 'user', 'student_id', 'name', 'courses']


# Course Enrollment serializer
class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = ['course', 'student', 'enrolled_at']


# Attendance serializer
class AttendanceSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    present_students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'course', 'date', 'present_students', 'lecturer_latitude', 'lecturer_longitude']


# Attendance token serializer
class AttendanceTokenSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = AttendanceToken
        fields = ['id', 'course', 'token', 'generated_at', 'expires_at', 'is_active']

# Logout serializer
class LogoutSerializer(serializers.Serializer):
    # A simple serializer to use in LogoutView, no fields needed for logout
    pass

# Submit Location serializer
class SubmitLocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    attendance_token = serializers.CharField()
