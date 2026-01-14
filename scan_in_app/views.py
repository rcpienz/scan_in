from django.shortcuts import render, redirect
from .models import TimeIn, Employee
from .forms import TimeInForm
from django.utils import timezone
from calendar import monthrange
from datetime import datetime
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.
def index(request):
    """Home page"""
    return render(request, "scan_in/index.html")


def timeIn(request):
    feedback = None  # For immediate feedback

    if request.method != "POST":
        # No data submitted; create a blank form.
        form = TimeInForm()
    else:
        # POST data submitted; process data.
        form = TimeInForm(data=request.POST)
        if form.is_valid():
            timeIn = form.save(commit=False)
            employee = form.cleaned_data["employeeObj"]
            timeIn.employee = employee
            now = timezone.localtime(timezone.now())
            timeIn.dateAdded = now

            # Determine lateness
            schedule = employee.schedule  # Assuming Employee has a schedule FK
            scheduled_time = timezone.datetime.combine(now.date(), schedule.startTime)
            scheduled_time = timezone.make_aware(scheduled_time)

            if now > scheduled_time + timezone.timedelta(
                minutes=schedule.grace_minutes
            ):
                timeIn.isLate = True
                delta = now - (
                    scheduled_time + timezone.timedelta(minutes=schedule.grace_minutes)
                )
                timeIn.lateMinutes = int(delta.total_seconds() // 60)
                feedback = {
                    "status": "LATE",
                    "color": "red",
                    "minutes": timeIn.lateMinutes,
                }
            else:
                timeIn.isLate = False
                timeIn.lateMinutes = 0
                feedback = {"status": "ON TIME", "color": "green", "minutes": 0}

            timeIn.save()

            # Render the same page with feedback
            form = TimeInForm()
    # Display a blank or invalid form.
    context = {"form": form, "feedback": feedback}
    return render(request, "scan_in/time-in.html", context)


@staff_member_required(login_url="/admin/login/")
def monthly_attendance(request):
    employees = Employee.objects.all().order_by("fName")

    selected_employee_id = request.GET.get("employee")
    month_param = request.GET.get("month")

    records = TimeIn.objects.none()
    employee = None
    summary = None

    # Handle Month
    if month_param:
        year, month = map(int, month_param.split("-"))
    else:
        now = timezone.localtime()
        year = now.year
        month = now.month

    startDate = timezone.make_aware(datetime(year, month, 1, 0, 0, 0))
    lastDay = monthrange(year, month)[1]
    endDate = timezone.make_aware(datetime(year, month, lastDay, 23, 59, 59))

    # Handle Employee
    if selected_employee_id:
        employee = Employee.objects.filter(id=selected_employee_id).first()

        if employee:
            records = TimeIn.objects.filter(
                employee=employee, dateAdded__range=(startDate, endDate)
            )

        total_days = records.count()
        late_days = records.filter(isLate=True).count()
        on_time_days = total_days - late_days
        total_late_minutes = (
            records.filter(isLate=True).aggregate(total=models.Sum("lateMinutes"))[
                "total"
            ]
            or 0
        )

        summary = {
            "total_days": total_days,
            "late_days": late_days,
            "on_time_days": on_time_days,
            "total_late_minutes": total_late_minutes,
        }

    context = {
        "employees": employees,
        "employee": employee,
        "records": records.order_by("dateAdded"),
        "summary": summary,
        "selected_employee_id": selected_employee_id,
        "selectedMonth": f"{year}-{month:02d}",
        "monthLabel": datetime(year, month, 1).strftime("%B %Y"),
    }

    return render(request, "scan_in/monthly_attendance.html", context)
