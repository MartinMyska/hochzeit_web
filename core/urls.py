from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('prijdeme/', views.rsvp, name='rsvp'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/csv/submissions/', views.csv_submissions, name='csv_submissions'),
    path('dashboard/csv/persons/', views.csv_persons, name='csv_persons'),
]
