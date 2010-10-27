from django.conf.urls.defaults import *
from django.contrib import admin

from djangosms.core.views import incoming
from djangosms.ui.urls import urlpatterns as ui_urls

from blaster.views import index
from blaster.views import updated
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^dashboard/', index),
    (r'^event/new/', new_event),
    (r'^masstext/send/', send_masstext),
    (r'^whitelist/', whitelist)
      
)
