from django.conf.urls import url

from . import views, controller

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pull/', controller.pull_purchases, name='pull'),
]