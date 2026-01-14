from django import forms
from .models import TimeIn, Employee
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta


class TimeInForm(forms.ModelForm):
    employeeId = forms.CharField(label="Enter Employee ID")

    class Meta:
        model = TimeIn
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        empId = cleaned_data.get("employeeId")

        if not empId:
            return

        employee = Employee.objects.filter(employeeId=empId).first()

        if not employee:
            raise forms.ValidationError("Employee ID does not exist")

        # validate Schedule
        if not employee.schedule:
            raise forms.ValidationError("Employee has no schedule assigned")

        now = timezone.localtime()
        today = now.date()

        # Already timed in?
        if TimeIn.objects.filter(employee=employee, dateAdded__date=today).exists():
            raise forms.ValidationError(f"{empId} has already timed in")

        # expecred time
        startTime = employee.schedule.startTime
        grace = employee.schedule.grace_minutes

        expectedDt = timezone.make_aware(
            datetime.combine(today, startTime)
        ) + timedelta(minutes=grace)

        lateMinutes = max(0, int((now - expectedDt).total_seconds() // 60))

        cleaned_data["employeeObj"] = employee
        cleaned_data["isLate"] = lateMinutes > 0
        cleaned_data["lateMinutes"] = lateMinutes

        return cleaned_data
