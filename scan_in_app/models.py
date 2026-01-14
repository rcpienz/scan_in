from django.db import models
from django.utils import timezone


# Create your models here.


class Schedule(models.Model):
    name = models.CharField(max_length=50)
    startTime = models.TimeField(verbose_name="Start Time")
    grace_minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name}({self.startTime})"


class Employee(models.Model):
    employeeId = models.CharField(
        max_length=50, unique=True, verbose_name="Employee ID"
    )
    fName = models.CharField(max_length=50, verbose_name="First Name")
    lName = models.CharField(max_length=50, verbose_name="Last Name")
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Schedule",
    )

    def __str__(self):
        return f"{self.employeeId} - {self.fName} {self.lName}"


class TimeIn(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    dateAdded = models.DateTimeField(default=timezone.now, verbose_name="Time In")
    isLate = models.BooleanField(default=False, verbose_name="Late?")
    lateMinutes = models.PositiveIntegerField(default=0, verbose_name="Late Minutes")

    class Meta:
        verbose_name = "Time In"
        verbose_name_plural = "Time In Records"

    @property
    def status(self):
        return "LATE" if self.isLate else "ON TIME"

    def __str__(self):
        return f"{self.employee.employeeId} - {self.status}"
