from django.urls import path
from . import views

from django.views.i18n import JavaScriptCatalog

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path('chart/line/', views.line_chart, name='line_chart'),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path('admin/customAdmin', views.customAdmin, name='customAdmin'),
    path('table/result', views.resultTable, name='resultTable'),
    path('table/runnerResults/<str:runnerId>', views.runnerResults, name='runnerResults'),
    path('authenticate/login', views.loginUser, name='loginUser'),
    # path('accounts/login', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='loginUser'),
]