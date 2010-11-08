from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from .views import *
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^dashboard/', login_required(index)),
    (r'^event/new/', login_required(new_event)),
    (r'^masstext/send/', login_required(send_masstext)),
    (r'^alerts/send/', login_required(send_alerts)),
    (r'^whitelist/', whitelist),
    (r'^contacts/(\d+)/delete/', login_required(delete_contact)),
    (r'^contacts/(\d+)/edit/', login_required(edit_contact)),
    (r'^contacts/(\d+)/view/', login_required(view_contact)),
    (r'^connections/(\d+)/add/', login_required(add_connection)),
    (r'^connections/(\d+)/edit/', login_required(edit_connection)),
    (r'^connections/(\d+)/view/', login_required(view_connections)),
)
