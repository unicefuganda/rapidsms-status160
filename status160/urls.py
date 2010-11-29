from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from .views import *
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^dashboard/', login_required(dashboard), name='status160-dashboard'),
    url(r'^event/new/', login_required(new_event)),
    url(r'^masstext/send/', login_required(send_masstext)),
    url(r'^alerts/send/', login_required(send_alerts)),
    url(r'^whitelist/', whitelist),
    url(r'^contacts/(\d+)/delete/', login_required(delete_contact)),
    url(r'^contacts/(\d+)/edit/', login_required(edit_contact)),
    url(r'^contacts/(\d+)/view/', login_required(view_contact)),
    url(r'^connections/(\d+)/add/', login_required(add_connection)),
    url(r'^connections/(\d+)/edit/', login_required(edit_connection)),
    url(r'^connections/(\d+)/delete/', login_required(delete_connection)),
    url(r'^connections/(\d+)/view/', login_required(view_connections)),
)
