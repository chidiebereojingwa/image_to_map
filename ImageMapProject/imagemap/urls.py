from django.urls import path
from . import views

app_name = 'imagemap'
urlpatterns = [
    path('', views.index, name='index'),
]
