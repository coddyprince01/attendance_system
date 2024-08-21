from rest_framework import serializers
from .models import Lecturer, Student, Course, CourseEnrollment, Attendance, AttendanceToken
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class LecturerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Lecturer
        fields = ['id', 'user', 'name']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'name']

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = CourseEnrollment
        fields = ['student', 'enrolled_at']

class CourseSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer()
    students = CourseEnrollmentSerializer(source='courseenrollment_set', many=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'course_code', 'lecturer', 'students']

class AttendanceSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    present_students = StudentSerializer(many=True)
    missed_students = StudentSerializer(many=True)

    class Meta:
        model = Attendance
        fields = ['id', 'course', 'date', 'present_students', 'missed_students']

class AttendanceTokenSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = AttendanceToken
        fields = ['id', 'course', 'token', 'generated_at', 'expires_at']
