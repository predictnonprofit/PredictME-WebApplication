from django.db import models
from membership.models import Member


class CrashReport(models.Model):
    CRASH_STATUS = (
        ("not_fixed", "Not Fixed"),
        ("fixed", "Fixed"),
        ("in_progress", "In Progress"),
    )
    member = models.ForeignKey(to=Member, on_delete=models.CASCADE, related_name="bug_reports")
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=150, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    file_attachment = models.FileField(upload_to="crash_reports/files", null=True, blank=True)
    screenshot = models.FileField(upload_to='crash_reports/screenshots', null=True, blank=True)
    is_seen = models.BooleanField(default=False)
    is_solved = models.BooleanField(default=False)
    crash_status = models.CharField(choices=CRASH_STATUS, max_length=20, null=True, blank=True,
                                    default=CRASH_STATUS[0][0])
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "crash_reports"
