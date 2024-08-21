from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'lecturers', views.LecturerViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'attendances', views.AttendanceViewSet)
router.register(r'attendance-tokens', views.AttendanceTokenViewSet)

urlpatterns = [
    
    path('', include(router.urls)),
]
