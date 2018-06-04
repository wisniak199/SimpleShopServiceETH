from django.conf.urls import url, include
from rest_framework import routers
from shop import views


urlpatterns = [
    url(r'^$', views.welcome, name='welcome'),
    url(r'^end_session/$', views.end_session, name='end-session'),
    url(r'^shop/$', views.shop, name='shop'),
    url(r'^start_session/$', views.start_session, name='start-session'),

]
