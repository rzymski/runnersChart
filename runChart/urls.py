from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('bar/', views.bar_chart, name='bar_chart'),
    path('line/', views.line_chart, name='line_chart'),
]
