from django.db import models
from django.contrib.auth.models import User




class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='lecturer_pictures/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=10, unique=True)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='courses')
    #students = models.ManyToManyField(Student, through='CourseEnrollment')
    students = models.ManyToManyField(Student, through='CourseEnrollment', related_name='courses')

    def __str__(self):
        return self.name

class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')

class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    present_students = models.ManyToManyField(Student, related_name='attended_classes')
    missed_students = models.ManyToManyField(Student, related_name='missed_classes')
    lecturer_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lecturer_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.course.name} - {self.date}"

    def is_within_radius(self, student_latitude, student_longitude, radius=100):
        """
        Checks if the student's location is within the specified radius (in meters) of the lecturer's location.
        """
        if self.lecturer_latitude is not None and self.lecturer_longitude is not None:
            from geopy.distance import geodesic
            lecturer_location = (self.lecturer_latitude, self.lecturer_longitude)
            student_location = (student_latitude, student_longitude)
            distance = geodesic(lecturer_location, student_location).meters
            return distance <= radius
        return False

class AttendanceToken(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    token = models.CharField(max_length=6, unique=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.course.name} - {self.token}"
