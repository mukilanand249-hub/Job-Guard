from django.db import models

class ScanHistory(models.Model):
    url = models.URLField(blank=True, null=True)
    text_content = models.TextField()
    trust_score = models.IntegerField()
    verdict = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.verdict} - {self.timestamp}"

class Blacklist(models.Model):
    url = models.URLField(unique=True)
    reason = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    report_count = models.IntegerField(default=1)

    def __str__(self):
        return self.url
