from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Lecturer, Student, Course, CourseEnrollment, Attendance, AttendanceToken
from .serializers import LecturerSerializer, StudentSerializer, CourseSerializer, AttendanceSerializer, AttendanceTokenSerializer
from django.utils import timezone
from django.http import HttpResponse
import csv
from rest_framework import permissions

class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAuthenticated]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def generate_attendance_token(self, request, pk=None):
        course = self.get_object()
        token = AttendanceToken.objects.create(course=course, token="ABCDE", expires_at=timezone.now() + timezone.timedelta(minutes=15))
        serializer = AttendanceTokenSerializer(token)
        return Response(serializer.data)

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

class AttendanceTokenViewSet(viewsets.ModelViewSet):
    queryset = AttendanceToken.objects.all()
    serializer_class = AttendanceTokenSerializer
    permission_classes = [IsAuthenticated]

class StudentEnrolledCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Course.objects.none()

        enrollments = CourseEnrollment.objects.filter(student=student)
        course_ids = enrollments.values_list('course_id', flat=True)
        return Course.objects.filter(id__in=course_ids)

class LecturerCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            lecturer = Lecturer.objects.get(user=user)
        except Lecturer.DoesNotExist:
            return Course.objects.none()

        return Course.objects.filter(lecturer=lecturer)
