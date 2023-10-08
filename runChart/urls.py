from django.urls import path
from . import views

from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("", views.index, name="index"),
    path('chart/line/', views.line_chart, name='line_chart'),

    path('test/xd', views.xd, name='xd'),
    path('test/form', views.form, name='myForm'),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),

    path('admin/customAdmin', views.customAdmin, name='customAdmin'),
    path('table/result', views.resultTable, name='resultTable'),
    path('table/runnerResults/<str:runnerId>', views.runnerResults, name='runnerResults'),

    # path('admin/add', views.adminAddRecord, name='adminAddRecord'),
]