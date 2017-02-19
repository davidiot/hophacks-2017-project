from django.conf.urls import url

from . import views, controller

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pull/', controller.pull_purchases, name='pull'),
    url(r'^spending/', controller.get_spending, name='spending'),
    url(r'^donate/', controller.make_donation, name='donate'),
    url(r'^uid/', controller.get_my_id, name='uid'),
    url(r'^mydonations/', controller.get_my_donations, name='mydonations'),
    url(r'^suggestions/', controller.get_displayed_suggestions,
        name='suggestions'),
    url(r'^charities/name/(?P<sect>\w{0,50})/$',
        controller.get_charities_by_name,
        name='filtercharitiesbyname'),
    url(r'^charities/id/(?P<id>[0-9])/$',
        controller.get_charities_by_id,
        name='filtercharitiesbyid')
]