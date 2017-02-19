from django.conf.urls import url

from . import views, controller

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pull/', controller.pull_purchases, name='pull'),
    url(r'^charities/name/(?P<sect>\w{0,50})/$',
        controller.get_charities_by_name,
        name='filtercharitiesbyname'),
    url(r'^charities/id/(?P<id>[0-9])/$',
        controller.get_charities_by_id,
        name='filtercharitiesbyid')
]