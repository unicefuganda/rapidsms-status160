from django.conf.urls.defaults import *
from django.contrib import admin

from generic.views import generic, generic_row
from contact.forms import FreeSearchForm, DistictFilterForm, MassTextForm
from generic.sorters import SimpleSorter
from .views import *
from .forms import CreateEventForm, SendAlertsForm, AgencyFilterForm, TeamFilterForm, OfficeFilterForm, WardenFilterForm
from .sorters import StatusSorter
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^dashboard/$', generic, {
      'model':Contact,
      'filter_forms':[WardenFilterForm, TeamFilterForm, AgencyFilterForm, OfficeFilterForm, FreeSearchForm],
      'action_forms':[MassTextForm, CreateEventForm, SendAlertsForm],
      'objects_per_page':25,
      'partial_row':'status160/partials/contact_row.html',
      'partial_header':'status160/partials/partial_header.html',
      'base_template':'status160/contacts_base.html',
      'columns':[('Name', True, 'name', SimpleSorter()),
                 ('Team', False, '', None,),
                 ('Agency', False, '', None,),
                 ('Location',True,'reporting_location__name', SimpleSorter(),),
                 ('Event',False,'', None,),
                 ('Status',True,'status', StatusSorter(),),
                 ('Warden',False,'', None,),
                 ('Comments',False,'', None,),
                 ('Last Message',False,'', None,),
                 ('',False,'',None,)],
    }, name='status160-dashboard'),
    url(r'^contacts/(?P<pk>\d+)/view/', generic_row, {'model':Contact, 'partial_row':'status160/partials/contact_row.html'}, name="status160-contact"),
    url(r'^whitelist/', whitelist),
    url(r'^contacts/(\d+)/delete/', delete_contact),
    url(r'^contacts/(\d+)/edit/', edit_contact),
    url(r'^contacts/add/', add_contact),
    url(r'^connections/(\d+)/add/', add_connection),
    url(r'^connections/(\d+)/edit/', edit_connection),
    url(r'^connections/(\d+)/delete/', delete_connection),
    url(r'^connections/(\d+)/view/', view_connections),
)
