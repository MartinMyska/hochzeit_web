from django.contrib import admin
from .models import RSVPSubmission, Person


class PersonInline(admin.TabularInline):
    model = Person
    extra = 0


@admin.register(RSVPSubmission)
class RSVPSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'submitted_at', 'accom_want', 'accom_pref', 'song_request')
    list_filter = ('accom_want',)
    ordering = ('-submitted_at',)
    inlines = [PersonInline]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'submission', 'is_child', 'age', 'diet', 'alcohol')
