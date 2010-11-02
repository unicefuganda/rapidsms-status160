from django.conf.urls.defaults import *
from django.contrib import admin

from .views import *
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^dashboard/', index),
    (r'^event/new/', new_event),
    (r'^masstext/send/', send_masstext),
    (r'^alerts/send/', send_alerts),
    (r'^whitelist/', whitelist),
    (r'^contacts/(\d+)/delete/', delete_contact),
    (r'^contacts/(\d+)/edit/', edit_contact),
    (r'^contacts/(\d+)/view/', view_contact),
    (r'^connections/(\d+)/add/', add_connection),
    (r'^connections/(\d+)/edit/', edit_connection),
    (r'^connections/(\d+)/view/', view_connections),
)
