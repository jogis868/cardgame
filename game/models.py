from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import random
import string

# Function to generate a unique room code
def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Custom User model with Teacher/Student roles
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    # Fixing the ManyToManyField conflicts with Django's built-in Group and Permissions
    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

# Room model that belongs to a Teacher
class Room(models.Model):
    code = models.CharField(max_length=6, unique=True, default=generate_room_code)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, null=True)  # <--- new field

# Card model associated with a Room
class Card(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="cards")
    front_text = models.CharField(max_length=255)  # Term
    back_text = models.TextField()  # Definition
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.front_text

# Student's performance tracking model
class StudentResult(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="results")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="student_results")
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.score} points"