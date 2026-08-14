from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hr.interfaces.api.views import (
    EmployeeViewSet,
    LeaveSummaryView,
    DepartmentMetricsView,
)

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")

urlpatterns = [
    path("", include(router.urls)),
    path("leave-summary/", LeaveSummaryView.as_view(), name="leave-summary"),
    path("department-metrics/", DepartmentMetricsView.as_view(), name="department-metrics"),
]
