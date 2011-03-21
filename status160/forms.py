from django.conf import settings
from django import forms
from rapidsms.models import Contact, Connection, ConnectionBase
from simple_locations.models import Area
from poll.models import Poll, ResponseCategory, Response, Category
from generic.forms import ActionForm, FilterForm
from django.db.models import Q
from operator import itemgetter
from .models import WardenRelationship, Team, Agency, Alert
from django.contrib.sites.models import Site
from rapidsms_httprouter.router import get_router
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.models import Backend
from status160.templatetags.status import status
import datetime

class WardenFilterForm(FilterForm):
    wardens = forms.ModelMultipleChoiceField(queryset=Contact.objects.filter(pk__in=WardenRelationship.objects.all().values_list('warden', flat=True)).order_by('name'), label="Show charges for:")

    def filter(self, request, queryset):
        wardens_pk = self.cleaned_data['wardens']
        query = None
        for warden in wardens_pk:
            if query:
                query = query | Q(pk__in=WardenRelationship.objects.get(warden=warden).dependents.all()) 
            else:
                query = Q(pk__in=WardenRelationship.objects.get(warden=warden).dependents.all())
        return queryset.filter(query)

class AgencyFilterForm(FilterForm):
    agencies = forms.ModelMultipleChoiceField(queryset=Agency.objects.all().order_by('name'), label="Show agencies:")

    def filter(self, request, queryset):
        groups_pk = self.cleaned_data['agencies']
        return queryset.filter(groups__in=groups_pk)

class TeamFilterForm(FilterForm):
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all().order_by('name'), label="Show teams:")

    def filter(self, request, queryset):
        groups_pk = self.cleaned_data['teams']
        return queryset.filter(groups__in=groups_pk)

class OfficeFilterForm(FilterForm):
    offices = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(kind__name='Office').order_by('name'), label="Show locations:")    

    def filter(self, request, queryset):
        locations_pk = self.cleaned_data['offices']
        return queryset.filter(reporting_location__in=locations_pk)

class CreateEventForm(ActionForm):
    short_description = forms.CharField(max_length=32, required=True, label="Short description:")
    text_question = forms.CharField(max_length=160, required=True, label="Text question for tracking this event:", help_text="(note: an affirmative response to this question should always indicate a positive status, i.e. safe, all-clear etc.)")
    action_label = 'Create'
    
    def perform(self, request, results):
        if request.user and request.user.has_perm('poll.add_poll'):
            contacts = results
            description = self.cleaned_data['short_description']
            user = request.user
            question = self.cleaned_data['text_question']
            poll = Poll.create_yesno(
                 description,
                 question,
                 '',
                 contacts,
                 user
            )
            poll.sites.add(Site.objects.get_current())
            yes_category = poll.categories.get(name='yes')
            yes_category.name = 'safe'
            yes_category.response = "We received your response as 'yes',please send any updates to the system if your situation changes or you have useful information to provide." 
            yes_category.priority = 4
            yes_category.color = '99ff77'
            yes_category.save()
            no_category = poll.categories.get(name='no')
            no_category.response = "We received your response as 'no',please send any updates to the system if your situation changes or you have useful information to provide."
            no_category.name = 'unsafe'
            no_category.priority = 1
            no_category.color = 'ff9977'
            no_category.save()
            unknown_category = poll.categories.get(name='unknown')
            unknown_category.default = False
            unknown_category.priority = 2
            unknown_category.color = 'ffff77'
            unknown_category.save()
            unclear_category = Category.objects.create(
                poll=poll,
                name='unclear',
                default=True,
                color='ffff77',
                response='We have recorded but did not understand your response,please repeat (with a yes or no response)',
                priority=3
            )
            poll.start()
            return ("Event created, messages sent!", 'success',)
        else:
            return ("You don't have permission to create events!", 'error',)

class SendAlertsForm(ActionForm):
    action_label = 'Send Alerts to Wardens'
    
    def perform(self, request, results):
        if not request.user.has_perm('status160.add_alert'):
            return ("You don't have permission to send alerts!", 'error',)
        try:
            alert = Alert.objects.latest('sent')
            td = datetime.datetime.now() - alert.sent
            total_seconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

            # don't spam like crazy
            if (total_seconds < 900):
                return ('An alert was sent in the past 15 minutes, please try later.', 'error',)
        except Alert.DoesNotExist:
            # first alert can be sent whenever
            pass

        alert = Alert()
        alert.save()

        for warden in WardenRelationship.objects.all():
            outstanding = []
            for dependent in warden.dependents.all():
                status_num = status(dependent, 'priority')
                if int(status_num) < 3:
                    outstanding.append((dependent, status_num))

            if (len(outstanding)):
                outstanding = sorted(outstanding, key=itemgetter(1), reverse=True)
                smstext = "%s persons still unaccounted for/unsafe:" % str(len(outstanding))
                text = smstext
                toadd = ''
                off = 0
                while (len(text) < 476) and (off < len(outstanding)):
                    smstext = text
                    if outstanding[off][0].default_connection:

                        text += "%s(%s)" % (outstanding[off][0].name, outstanding[off][0].default_connection.identity)
                    else:
                        text +="%s" % outstanding[off][0].name
                    if off < (len(outstanding) - 1):
                        text += ','
                    off += 1

                if off == len(outstanding) and len(text) < 476:
                    smstext = text
                if off < len(outstanding):
                    smstext += '...'

                router = get_router()
                for conn in Connection.objects.filter(contact=warden.warden):
                    outgoing = OutgoingMessage(conn, smstext)
                    router.handle_outgoing(outgoing)
        return ('Alerts sent!', 'success',)

class EditContactForm(forms.Form): # pragma: no cover
    
    name = forms.CharField(max_length=100, required=True)
    warden = forms.ModelChoiceField(queryset=Contact.objects.filter(pk__in=WardenRelationship.objects.all().values_list('warden', flat=True)).order_by('name'), required=False)
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all().order_by('name'), required=False)
    agencies = forms.ModelMultipleChoiceField(queryset=Agency.objects.all().order_by('name'), required=False)
    location = forms.ModelChoiceField(queryset=Area.objects.filter(kind__name='Office'), required=False)
    comments = forms.CharField(max_length=2000, required=False, widget=forms.Textarea(attrs={'rows': 2}))
    
    def __init__(self, data=None, **kwargs):
        kwargs.setdefault('poll', None)
        poll = kwargs.pop('poll')
        kwargs.setdefault('contact', None)
        contact = kwargs.pop('contact')
        if data:
            if poll:
                if poll.comments.filter(user=contact).count():
                    # if this is from a POST, the dictionary is immutable
                    # and won't like being updated
                    try:
                        data.update({'comments':poll.comments.filter(user=contact)[0].text})
                    except:
                        pass
            forms.Form.__init__(self, data, **kwargs)
        else:
            forms.Form.__init__(self, **kwargs)
        if poll:
            self.fields['status'] = forms.ModelChoiceField(required=True, queryset=poll.categories.all()) 

class NewContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    warden = forms.ModelChoiceField(queryset=Contact.objects.filter(pk__in=WardenRelationship.objects.all().values_list('warden', flat=True)).order_by('name'), required=False)
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all().order_by('name'), required=False)
    agencies = forms.ModelMultipleChoiceField(queryset=Agency.objects.all().order_by('name'), required=False)
    location = forms.ModelChoiceField(queryset=Area.objects.filter(kind__name='Office'), required=False)
    identity = forms.CharField(max_length=15, required=True, label="Primary contact information")
    is_warden = forms.BooleanField(required=False, initial=False)

class ConnectionForm(forms.Form): # pragma: no cover
    identity = forms.CharField(max_length=15)
