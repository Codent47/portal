from django.db import models
from django.contrib.auth.models import User
import os
import re
from django.utils import timezone
DEPARTMENTS = (
    ('CS', 'CS'),
    ('MATHS','MATHS')
)

class Hod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    department = models.CharField(max_length=5, choices=DEPARTMENTS, null=True, blank=True)

    def __str__(self):
        return self.name

class Faculty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Leave(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    department = models.CharField(max_length=5, choices=DEPARTMENTS, null=True, blank=True)
    dateTimeStart = models.DateTimeField()
    dateTimeEnd = models.DateTimeField()
    reason = models.TextField()
    corrAddress = models.TextField()
    corrPhone = models.CharField(max_length=15)
    approved = models.BooleanField(default=0, blank=True)
    disapproved = models.BooleanField(default=0, blank=True)
    inprocess = models.BooleanField(default=1, blank=True)
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        return self.student.bitsId + ' '+ self.student.name + ' ' + str(self.id)

class Transcript(models.Model):
    bitsID = models.CharField(max_length=13,null=True, blank=True)
    corrEmail = models.CharField(max_length=50)
    refNo = models.CharField(max_length=20)
    approved = models.BooleanField(default=0, blank=True)
    disapproved = models.BooleanField(default=0, blank=True)
    inprocess = models.BooleanField(default=1, blank=True)
    dupTranscripts = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.bitsID + ' '+ self.refNo



