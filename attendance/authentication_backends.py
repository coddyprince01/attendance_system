from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from attendance.models import Student, Lecturer

class StudentBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            student = Student.objects.get(user__username=username) or Student.objects.get(user__email=username) or Student.objects.get(id_number=username)
        except Student.DoesNotExist:
            return None

        if student.user.check_password(password):
            return student.user
        return None

class StaffBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            staff = Lecturer.objects.get(user__username=username) or Lecturer.objects.get(user__email=username) or Lecturer.objects.get(staff_id=username)
        except Lecturer.DoesNotExist:
            return None

        if staff.user.check_password(password):
            return staff.user
        return None
