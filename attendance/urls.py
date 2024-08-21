from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LecturerViewSet, StudentViewSet, CourseViewSet, AttendanceViewSet, AttendanceTokenViewSet, StudentEnrolledCoursesView, LecturerCoursesView

router = DefaultRouter()
router.register(r'lecturers', LecturerViewSet)
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'attendance-tokens', AttendanceTokenViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('student/courses/', StudentEnrolledCoursesView.as_view(), name='student-courses'),
    path('lecturer/courses/', LecturerCoursesView.as_view(), name='lecturer-courses'),
]
