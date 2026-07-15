from django.db import models


class RSVPSubmission(models.Model):
    accom_want = models.CharField(max_length=10, blank=True)
    accom_pref = models.CharField(max_length=200, blank=True)
    song_request = models.CharField(max_length=300, blank=True)
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        first = self.persons.first()
        name = first.name if first else '—'
        return f"#{self.pk} {name} ({self.submitted_at:%Y-%m-%d %H:%M})"


class Person(models.Model):
    submission = models.ForeignKey(RSVPSubmission, on_delete=models.CASCADE, related_name='persons')
    name = models.CharField(max_length=200)
    is_child = models.BooleanField(default=False)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    diet = models.CharField(max_length=500, blank=True)
    other_diet = models.CharField(max_length=300, blank=True)
    alcohol = models.CharField(max_length=500, blank=True)

    def __str__(self) -> str:
        return self.name
