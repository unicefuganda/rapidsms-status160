from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from generic.views import generic, generic_row
from contact.forms import FreeSearchForm, DistictFilterForm, MassTextForm
from generic.sorters import SimpleSorter
from .views import *
from .forms import CreateEventForm, SendAlertsForm, AgencyFilterForm, TeamFilterForm, OfficeFilterForm, WardenFilterForm
admin.autodiscover()

urlpatterns = patterns(
    '',
#    url(r'^dashboard/', login_required(dashboard), name='status160-dashboard'),
    url(r'^dashboard2/$', login_required(generic), {
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
                 ('Status',False,'', None,),
                 ('Warden',False,'', None,),
                 ('Comments',False,'', None,),
                 ('Last Message',False,'', None,),
                 ('',False,'',None,)],
    }, name='status160-dashboard'),
    url(r'^contacts/(?P<pk>\d+)/view/', generic_row, {'model':Contact, 'partial_row':'status160/partials/contact_row.html'}),
#    url(r'^event/new/', login_required(new_event)),
#    url(r'^masstext/send/', login_required(send_masstext)),
#    url(r'^alerts/send/', login_required(send_alerts)),
    url(r'^whitelist/', whitelist),
    url(r'^contacts/(\d+)/delete/', login_required(delete_contact)),
    url(r'^contacts/(\d+)/edit/', login_required(edit_contact)),
    url(r'^contacts/add/', login_required(add_contact)),
#    url(r'^contacts/(\d+)/view/', login_required(view_contact)),
    url(r'^connections/(\d+)/add/', login_required(add_connection)),
    url(r'^connections/(\d+)/edit/', login_required(edit_connection)),
    url(r'^connections/(\d+)/delete/', login_required(delete_connection)),
    url(r'^connections/(\d+)/view/', login_required(view_connections)),
)
