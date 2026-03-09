from django.db import models
from django.contrib.auth.models import User

class Issue(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    CATEGORY_CHOICES = [
        ('Infrastructure', 'Infrastructure'),
        ('Safety', 'Safety'),
        ('Discipline', 'Discipline'),
        ('Academic', 'Academic'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    is_confidential = models.BooleanField(default=False)
    image = models.ImageField(upload_to='issue_images/', blank=True, null=True)

    # The Admin Comment field is now OUTSIDE the list, correctly placed here
    admin_comment = models.TextField(blank=True, null=True, help_text="Notes from the administration")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title