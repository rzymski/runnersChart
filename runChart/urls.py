from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('line/', views.line_chart, name='line_chart'),
]
