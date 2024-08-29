from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate, logout
from .models import Lecturer, Student, Course, Attendance, AttendanceToken
from .serializers import (
    LecturerSerializer, 
    StudentSerializer, 
    CourseSerializer, 
    AttendanceSerializer, 
    AttendanceTokenSerializer,
    LogoutSerializer,
    SubmitLocationSerializer
)
from django.utils import timezone
from django.http import HttpResponse
import csv

# Lecturer ViewSet
class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAuthenticated]

# Student ViewSet
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

# Course ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def generate_attendance_token(self, request, pk=None):
        course = self.get_object()
        token = AttendanceToken.objects.create(
            course=course, 
            token="ABCDE", 
            expires_at=timezone.now() + timezone.timedelta(minutes=15)
        )
        serializer = AttendanceTokenSerializer(token)
        return Response(serializer.data)

# Attendance ViewSet
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def generate_csv(self, request):
        course_id = request.query_params.get('course_id')
        date = request.query_params.get('date')
        attendances = Attendance.objects.filter(course_id=course_id, date=date)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

        writer = csv.writer(response)
        writer.writerow(['Student Name', 'Present'])

        for attendance in attendances:
            for student in attendance.present_students.all():
                writer.writerow([student.name, 'Yes'])
            for student in attendance.missed_students.all():
                writer.writerow([student.name, 'No'])

        return response

# AttendanceToken ViewSet
class AttendanceTokenViewSet(viewsets.ModelViewSet):
    queryset = AttendanceToken.objects.all()
    serializer_class = AttendanceTokenSerializer
    permission_classes = [IsAuthenticated]

# Student Enrolled Courses View
class StudentEnrolledCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        student = Student.objects.get(user=user)
        return Course.objects.filter(students=student)

# Custom Login Views
class StudentLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        student_id = request.data.get('student_id')

        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'student'):
            student = user.student
            if student.student_id == student_id:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'username': user.username,
                    'student_id': student.student_id
                })
            else:
                return Response({'error': 'Invalid student ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class StaffLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        staff_id = request.data.get('staff_id')

        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'lecturer'):
            lecturer = user.lecturer
            if lecturer.staff_id == staff_id:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'username': user.username,
                    'staff_id': lecturer.staff_id
                })
            else:
                return Response({'error': 'Invalid staff ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Logout View
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer  # Added serializer_class
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)

# Location-based Attendance View
class SubmitLocationView(generics.GenericAPIView):
    serializer_class = SubmitLocationSerializer  # Added serializer_class
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        attendance_token = request.data.get('attendance_token')
        
        try:
            token = AttendanceToken.objects.get(token=attendance_token, is_active=True)
        except AttendanceToken.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance = Attendance.objects.filter(course=token.course, date=timezone.now().date()).first()
        
        if attendance and attendance.is_within_radius(float(latitude), float(longitude)):
            user = request.user
            if hasattr(user, 'student'):
                student = user.student
                if student in token.course.students.all():
                    attendance.present_students.add(student)
                    attendance.save()
                    return Response({'status': 'Attendance marked successfully'}, status=status.HTTP_200_OK)
            return Response({'error': 'Student not enrolled in this course'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Location is out of range'}, status=status.HTTP_400_BAD_REQUEST)
