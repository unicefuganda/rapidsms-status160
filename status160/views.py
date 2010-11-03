from django.db import transaction
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.conf import settings
from django import forms
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from operator import itemgetter
from rapidsms.models import Contact, Connection, ConnectionBase
from .models import WardenRelationship, Team, Agency, Alert, Comments
from simple_locations.models import Area
from poll.models import Poll, Category, ResponseCategory, Response
from django.contrib.sites.models import Site
from rapidsms_httprouter.router import get_router
from rapidsms_httprouter.models import Message
from rapidsms.messages.outgoing import OutgoingMessage
from djtables import Table, Column
from status160.templatetags.status import status
import datetime

class FilterContactForm(forms.Form): # pragma: no cover
    
    wardens = forms.ModelMultipleChoiceField(queryset=Contact.objects.filter(pk__in=WardenRelationship.objects.all().values_list('warden', flat=True)).order_by('name'), required=False)
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all().order_by('name'), required=False)
    agencies = forms.ModelMultipleChoiceField(queryset=Agency.objects.all().order_by('name'), required=False)
    locations = forms.ModelMultipleChoiceField(queryset=Area.objects.all().order_by('name'), required=False)
    search_string = forms.CharField(max_length=1000, required=False)
    
class MassTextForm(forms.Form):
    text = forms.CharField(max_length=160, required=True)
    
class CreateEventForm(forms.Form):
    short_description = forms.CharField(max_length=32, required=True)
    text_question = forms.CharField(max_length=160, required=True)

class ContactsForm(forms.Form):
    contacts = forms.ModelMultipleChoiceField(queryset=Contact.objects.all(), widget=forms.CheckboxSelectMultiple())

def index(request):
    masstextform = MassTextForm()
    createventform = CreateEventForm()
    selected = False
    if request.method == 'POST':
        form = FilterContactForm(request.POST)
        if form.is_valid():
            wardens = form.cleaned_data['wardens']
            teams = form.cleaned_data['teams']
            agencies = form.cleaned_data['agencies']
            locations = form.cleaned_data['locations']
            search_string = form.cleaned_data['search_string']

            contacts = _filter_contacts(wardens, teams, agencies, locations, search_string)
            selected = True
        else:
            # no required fields, invalid field means something funky happened
            return HttpResponse(status=404)
    else:
        form = FilterContactForm()
        contacts = Contact.objects.all() 
    return render_to_response(
                "status160/index.html", 
                {'form':form, 
                 'contacts':contacts,
                 'masstextform':masstextform,
                 'createeventform':createventform,
                 'selected': selected,
                 }, RequestContext(request)) 


def whitelist(request):
    return render_to_response(
    "status160/whitelist.txt", 
    {'connections': Connection.objects.filter(contact__in=Contact.objects.all()).distinct()},
    mimetype="text/plain",
    context_instance=RequestContext(request))

@require_POST
def new_event(request):
    response = None
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        contacts_form = ContactsForm(request.POST)
        if form.is_valid() and contacts_form.is_valid():
            contacts = contacts_form.cleaned_data['contacts']
            poll = Poll.create_yesno(
                 form.cleaned_data['short_description'],
                 form.cleaned_data['text_question'],
                 '',
                 contacts,
                 request.user
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
            print "sending a response"
            response = "Event created, messages sent!"
            form = CreateEventForm()
        elif not contacts_form.is_valid():
            form.errors.setdefault('short_description', ErrorList())
            form.errors['short_description'].append('A status survey must have contacts.')
        
    else:
        form = CreateEventForm()
    return render_to_response("status160/event.html", {'createeventform':form, 'response':response},context_instance=RequestContext(request))    

@require_POST
def send_masstext(request):
    response = None
    if request.method == 'POST':
        form = MassTextForm(request.POST)
        contacts_form = ContactsForm(request.POST)
        if form.is_valid() and contacts_form.is_valid():
            connections = Connection.objects.filter(contact__in=contacts_form.cleaned_data['contacts']).distinct()
            router = get_router()
            for conn in connections:
                outgoing = OutgoingMessage(conn, form.cleaned_data['text'])
                router.handle_outgoing(outgoing)
            response = "Messages Sent!"
            form = MassTextForm()
        elif not contacts_form.is_valid():
            form.errors.setdefault('text', ErrorList())
            form.errors['text'].append('A set of recipients is required.')            
    else:
        form = MassTextForm()
    return render_to_response("status160/masstext.html", {'masstextform':form, 'response':response},context_instance=RequestContext(request))

@require_POST
def send_alerts(request):
#    if not request.user.has_perm('status160.add_alert'):
#        return Response(status=412)
    try:
        alert = Alert.objects.latest('sent')
        td = datetime.datetime.now() - alert.sent
        total_seconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        
        # don't spam like crazy
        if (total_seconds < 900):
            return HttpResponse(content='<span style="color:red">An alert was sent in the past 15 minutes, please try later.</span>', status=200)   
    except Alert.DoesNotExist:
        # first alert can be sent whenever
        pass
        
    alert = Alert()
    alert.save()
    
    for warden in WardenRelationship.objects.all():
        outstanding = []
        for dependent in warden.dependents.all():
            status_num = status(dependent, 'number')
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
            print "sending '%s'" % smstext

            router = get_router()
            for conn in Connection.objects.filter(contact=warden.warden):
                outgoing = OutgoingMessage(conn, smstext)
                router.handle_outgoing(outgoing)

    return HttpResponse(content='<span style="color:green">Alerts Sent!</span>', status=200)

@require_POST
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    contact.delete()
    return HttpResponse(status=200)

class EditContactForm(forms.Form): # pragma: no cover
    
    name = forms.CharField(max_length=100, required=True)
    warden = forms.ModelChoiceField(queryset=Contact.objects.filter(pk__in=WardenRelationship.objects.all().values_list('warden', flat=True)).order_by('name'), required=False)
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all().order_by('name'), required=False)
    agencies = forms.ModelMultipleChoiceField(queryset=Agency.objects.all().order_by('name'), required=False)
    location = forms.ModelChoiceField(queryset=Area.objects.all(), required=False)
    comments = forms.CharField(max_length=2000, required=False, widget=forms.Textarea(attrs={'rows': 2}))
    
    def __init__(self, data=None, **kwargs):
        kwargs.setdefault('poll', None)
        poll = kwargs.pop('poll')
        kwargs.setdefault('contact', None)
        contact = kwargs.pop('contact')
        if data:
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
            initial_category = poll.categories.get(name='unknown')  
            try:
                r = ResponseCategory.objects.filter(response__poll=poll, response__message__connection__contact=contact, is_override=True).latest('response__message__date')
                initial_category = r.category
            except ResponseCategory.DoesNotExist:
                try:
                    r = ResponseCategory.objects.filter(response__poll=poll, response__message__connection__contact=contact).latest('response__message__date')
                except ResponseCategory.DoesNotExist:
                    pass
            self.fields['status'] = forms.ModelChoiceField(required=True, queryset=poll.categories.all(), initial=initial_category) 

def edit_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    try:
        poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
    except Poll.DoesNotExist:
        poll = None
    if request.method == 'POST':
        contact_form = EditContactForm(request.POST, poll=poll, contact=contact)
        if contact_form.is_valid():
            contact.name = contact_form.cleaned_data['name']
            wardenrel = contact.charges.all()[0]
            wardenrel.warden = contact_form.cleaned_data['warden']
            wardenrel.save()
            contact.groups.clear()
            for t in contact_form.cleaned_data['teams']:
                contact.groups.add(t)
            for a in contact_form.cleaned_data['agencies']:
                contact.groups.add(a)
            contact.reporting_location = contact_form.cleaned_data['location']
            if poll:
                if poll.comments.filter(user=contact).count():
                    comments = poll.comments.filter(user=contact)[0]
                    comments.text = contact_form.cleaned_data['comments']
                    comments.save()
                else:
                    comments = Comments.objects.create(event=poll, user=contact, text=contact_form.cleaned_data['comments'])
                status = contact_form.cleaned_data['status']
                if Response.objects.filter(poll=poll, message__connection__contact=contact).count():
                    r = Response.objects.filter(poll=poll, message__connection__contact=contact).latest('message__date')
                    r.categories.add(ResponseCategory.objects.create(response=r, is_override=True, user=request.user, category=status))
                else:
                    m = Message.objects.create(connection=contact.default_connection, text='Status override from web', status='C', direction='I')
                    r = Response.objects.create(message=m, poll=poll)
                    r.categories.add(ResponseCategory.objects.create(response=r, is_override=True, user=request.user, category=status))                    
            contact.save()

            return render_to_response("status160/contact_row_view.html", {'contact':contact})
        else:
            return render_to_response("status160/contact_row_edit.html", {'contact':contact, 'form':contact_form},context_instance=RequestContext(request))    

    else:
        teams = []
        agencies = []
        poll = None
        try:
            poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
        except Poll.DoesNotExist:
            pass
        for g in contact.groups.all():
            try:
                agencies.append(g.agency)
            except Agency.DoesNotExist:
                try:
                    teams.append(g.team)
                except Team.DoesNotExist:
                    pass
        contact_form = EditContactForm({
            'name':contact.name,
            'warden': contact.charges.all()[0].warden,
            'teams': teams,
            'agencies': agencies,
            'location': contact.reporting_location,
        }, poll=poll, contact=contact)
        return render_to_response("status160/contact_row_edit.html", {'contact':contact, 'form':contact_form},context_instance=RequestContext(request))


def view_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    return render_to_response("status160/contact_row_view.html", {'contact':contact },RequestContext(request))

class ConnectionForm(forms.ModelForm): # pragma: no cover
    class Meta:
        model = Connection
        fields = ('identity','backend',)

def edit_connection(request, connection_id):
    connection = get_object_or_404(Connection, pk=connection_id)
    if request.method == 'POST':
        form = ConnectionForm(request.POST, instance=connection)
        if form.is_valid():
            form.save()
            return render_to_response("status160/connection_view.html", {'contact':connection.contact },context_instance=RequestContext(request))
    else:
        form = ConnectionForm(instance = connection)
    return render_to_response("status160/connection_edit.html", {'contact':connection.contact, 'form':form, 'connection':connection},context_instance=RequestContext(request))

def add_connection(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    if request.method == 'POST':
        form = ConnectionForm(request.POST)
        if form.is_valid():
            connection = form.save()
            connection.contact = contact
            connection.save()
            return render_to_response("status160/connection_view.html", {'contact':contact },context_instance=RequestContext(request))
    else:
        form = ConnectionForm()
    return render_to_response("status160/connection_edit.html", {'contact':contact, 'form':form },context_instance=RequestContext(request))

def view_connections(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    return render_to_response("status160/connection_view.html", {'contact':contact},context_instance=RequestContext(request))

def _filter_contacts(wardens, teams, agencies, locations, search_string):
    contacts = Contact.objects.all()
    query = None
    if len(wardens):
        for warden in wardens:
            if query:
                query = query | Q(pk__in=WardenRelationship.objects.get(warden=warden).dependents.all()) 
            else:
                query = Q(pk__in=WardenRelationship.objects.get(warden=warden).dependents.all())
        contacts = contacts.filter(query)
    if len(teams):
        contacts = contacts.filter(groups__in=teams)
    if len(agencies):
        contacts = contacts.filter(groups__in=agencies)
    if len(locations):
        contacts = contacts.filter(reporting_location__in=locations)
    if search_string:
            pks = []
            # split terms if the "OR" operator is used
            terms = [term.strip() for term in search_string.lower().split(' or ')]        
            return contacts.filter(
                (reduce(
                    lambda x, y: x | y,
                    [(Q(name__icontains=term) |
                      Q(groups__name__icontains=term))
                     for term in terms]
                ))).distinct()

    return contacts
