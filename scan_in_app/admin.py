from django.contrib import admin

# Register your models here.
from .models import TimeIn, Employee, Schedule


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employeeId", "fName", "lName", "schedule")
    search_fields = ("employeeId", "fName", "lName")
    list_filter = ("schedule",)


@admin.register(TimeIn)
class TimeInAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "dateAdded",
        "isLate",
        "lateMinutes",
    )
    list_filter = ("isLate", "dateAdded")
    search_fields = ("employee__employeeId",)
    date_hierarchy = "dateAdded"


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("name", "startTime", "grace_minutes")
