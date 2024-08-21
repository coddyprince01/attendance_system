from rest_framework import serializers
from .models import Lecturer, Student, Course, CourseEnrollment, Attendance, AttendanceToken
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class LecturerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Lecturer
        fields = ['id', 'user', 'name', 'profile_picture', 'courses']

    def get_courses(self, obj):
        courses = Course.objects.filter(lecturer=obj)
        return CourseSerializer(courses, many=True).data

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'name', 'courses']

    def get_courses(self, obj):
        enrollments = CourseEnrollment.objects.filter(student=obj)
        courses = [enrollment.course for enrollment in enrollments]
        return CourseSerializer(courses, many=True).data

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = CourseEnrollment
        fields = ['student', 'enrolled_at']

class CourseSerializer(serializers.ModelSerializer):
    lecturer = serializers.StringRelatedField()  # Changed to StringRelatedField to avoid recursion issues
    students = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'course_code', 'lecturer', 'students']

    def get_students(self, obj):
        enrollments = CourseEnrollment.objects.filter(course=obj)
        students = [enrollment.student for enrollment in enrollments]
        return StudentSerializer(students, many=True).data

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
