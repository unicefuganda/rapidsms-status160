from django.db import transaction
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.conf import settings
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from rapidsms.models import Contact, Connection
from .models import WardenRelationship, Team, Agency, Alert, Comments
from simple_locations.models import Area
from poll.models import Poll, ResponseCategory, Response
from rapidsms_httprouter.models import Message
import datetime
from .forms import FilterContactForm, MassTextForm, CreateEventForm, ContactsForm, EditContactForm, ConnectionForm
from .utils import create_status_survey, send_mass_text, send_alert, filter_contacts, assign_backend
from status160 import templatetags

def index(request):
    return render_to_response("status160/index.html", {}, RequestContext(request)) 

def dashboard(request):
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

            contacts = filter_contacts(wardens, teams, agencies, locations, search_string)
            selected = True
        else:
            # no required fields, invalid field means something funky happened
            return HttpResponse(status=404)
    else:
        form = FilterContactForm()
        contacts = Contact.objects.all() 
    return render_to_response(
                "status160/dashboard.html", 
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
            poll = create_status_survey(
                form.cleaned_data['short_description'],
                form.cleaned_data['text_question'], 
                contacts, 
                request.user)
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
            send_mass_text(contacts_form.cleaned_data['contacts'], form.cleaned_data['text'])
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

    send_alert()

    return HttpResponse(content='<span style="color:green">Alerts Sent!</span>', status=200)

@require_POST
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    contact.delete()
    return HttpResponse(status=200)

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
            if contact_form.cleaned_data['warden']:
                old_wardenrel = WardenRelationship.objects.filter(dependents=contact)
                if old_wardenrel.count():
                    for w in old_wardenrel:
                        w.dependents.remove(contact)

                wardenrel = WardenRelationship.objects.get(warden=contact_form.cleaned_data['warden'])
                wardenrel.dependents.add(contact)
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
                response = Response.objects.create(contact=contact,poll=poll)
                response.save()
                response.categories.add(ResponseCategory.objects.create(response=response, is_override=True, user=request.user, category=status))
            contact.save()

            return render_to_response("status160/contact_row_view.html", {'contact':contact},RequestContext(request))
        else:
            return render_to_response("status160/contact_row_edit.html", {'contact':contact, 'form':contact_form},context_instance=RequestContext(request))    

    else:
        teams = Team.objects.filter(id__in=contact.groups.all())
        agencies = Agency.objects.filter(id__in=contact.groups.all())
        poll = None
        try:
            poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
        except Poll.DoesNotExist:
            pass

        if contact.charges.count():
            warden = contact.charges.all()[0].warden
        else:
            warden = None
        contact_form = EditContactForm({
            'name':contact.name,
            'warden': warden,
            'teams': teams,
            'agencies': agencies,
            'location': contact.reporting_location,
            'status': templatetags.status.status(contact),
        }, poll=poll, contact=contact)
        return render_to_response("status160/contact_row_edit.html", {'contact':contact, 'form':contact_form},RequestContext(request))

def view_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    return render_to_response("status160/contact_row_view.html", {'contact':contact },RequestContext(request))

def edit_connection(request, connection_id):
    connection = get_object_or_404(Connection, pk=connection_id)
    if request.method == 'POST':
        form = ConnectionForm(request.POST)
        if form.is_valid():
            identity = form.cleaned_data['identity']
            identity, backend = assign_backend(str(identity))
            connection.identity = identity
            connection.backend = backend
            connection.save()
            return render_to_response("status160/connection_view.html", {'contact':connection.contact },context_instance=RequestContext(request))
    else:
        form = ConnectionForm({'identity':connection.identity})
    return render_to_response("status160/connection_edit.html", {'contact':connection.contact, 'form':form, 'connection':connection},context_instance=RequestContext(request))

def delete_connection(request, connection_id):
    connection = get_object_or_404(Connection, pk=connection_id)
    connection.delete()
    return render_to_response("status160/connection_view.html", {'contact':connection.contact },context_instance=RequestContext(request))

def add_connection(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    if request.method == 'POST':
        form = ConnectionForm(request.POST)
        if form.is_valid():
            identity = form.cleaned_data['identity']
            identity, backend = assign_backend(str(identity))
            connection = Connection.objects.create(identity=identity, backend=backend, contact=contact)
            return render_to_response("status160/connection_view.html", {'contact':contact },context_instance=RequestContext(request))
    else:
        form = ConnectionForm()
    return render_to_response("status160/connection_edit.html", {'contact':contact, 'form':form },context_instance=RequestContext(request))

def view_connections(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    return render_to_response("status160/connection_view.html", {'contact':contact},context_instance=RequestContext(request))

