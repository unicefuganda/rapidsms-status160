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
from poll.models import Poll, ResponseCategory, Response
from rapidsms_httprouter.models import Message
import datetime
from .utils import assign_backend
from .forms import ConnectionForm, EditContactForm, NewContactForm
from status160 import templatetags
from django.conf import settings
from urllib2 import urlopen
from django.contrib.auth.decorators import login_required

def index(request):
    return render_to_response("status160/index.html", {}, RequestContext(request)) 

def whitelist(request):
    return render_to_response(
    "status160/whitelist.txt", 
    {'connections': Connection.objects.filter(contact__in=Contact.objects.all()).distinct()},
    mimetype="text/plain",
    context_instance=RequestContext(request))

def _reload_whitelists():
    refresh_urls = getattr(settings, 'REFRESH_WHITELIST_URL', None)
    if refresh_urls is not None:
        if not type(refresh_urls) == list:
            refresh_urls = [refresh_urls,]
        for refresh_url in refresh_urls:
            try:
                status_code = urlopen(refresh_url).getcode()
                if int(status_code/100) == 2:
                    continue
                else:
                    return False
            except Exception as e:
                return False
        return True
    return False

@require_POST
@login_required
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    for conn in contact.connection_set.all():
        conn.delete()
    _reload_whitelists()
    contact.delete()
    return HttpResponse(status=200)

@login_required
def add_contact(request):
    form = NewContactForm()
    if request.method == 'POST':
        form = NewContactForm(request.POST)
        if form.is_valid():
            contact = Contact.objects.create(name=form.cleaned_data['name'])
            identity = form.cleaned_data['identity']
            identity, backend = assign_backend(str(identity))
            connection, created = Connection.objects.get_or_create(identity=identity, backend=backend)
            connection.contact = contact
            connection.save()

            warden = form.cleaned_data['warden']
            teams = form.cleaned_data['teams']
            agencies = form.cleaned_data['agencies']
            location = form.cleaned_data['location']
            is_warden = form.cleaned_data['is_warden']

            contact.reporting_location = location
            for t in teams:
                contact.groups.add(t)

            for a in agencies:
                contact.groups.add(a)

            if warden:
                wrel = WardenRelationship.objects.get(warden=warden)
                wrel.dependents.add(contact)

            if is_warden:
                WardenRelationship.objects.create(warden=contact)

            _reload_whitelists()
            return render_to_response('status160/partials/contact_row.html', {'object':contact, 'selectable':True}, RequestContext(request))

    return render_to_response("status160/partials/new_contact.html",{'form':form},RequestContext(request))

@login_required
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
            _reload_whitelists()
            return render_to_response("status160/partials/contact_row.html", {'object':contact, 'selectable':True},RequestContext(request))
        else:
            return render_to_response("status160/partials/contact_row_edit.html", {'contact':contact, 'form':contact_form},context_instance=RequestContext(request))    

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
        return render_to_response("status160/partials/contact_row_edit.html", {'contact':contact, 'form':contact_form},RequestContext(request))

@login_required
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
            _reload_whitelists()
            return render_to_response("status160/partials/connection_view.html", {'object':connection.contact },context_instance=RequestContext(request))
    else:
        form = ConnectionForm({'identity':connection.identity})
    return render_to_response("status160/partials/connection_edit.html", {'contact':connection.contact, 'form':form, 'connection':connection},context_instance=RequestContext(request))

@login_required
def delete_connection(request, connection_id):
    connection = get_object_or_404(Connection, pk=connection_id)
    connection.delete()
    _reload_whitelists()
    return render_to_response("status160/partials/connection_view.html", {'object':connection.contact },context_instance=RequestContext(request))

@login_required
def add_connection(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    if request.method == 'POST':
        form = ConnectionForm(request.POST)
        if form.is_valid():
            identity = form.cleaned_data['identity']
            identity, backend = assign_backend(str(identity))
            connection, created = Connection.objects.get_or_create(identity=identity, backend=backend)
            connection.contact = contact
            connection.save()
            _reload_whitelists()
            return render_to_response("status160/partials/connection_view.html", {'object':contact },context_instance=RequestContext(request))
    else:
        form = ConnectionForm()
    return render_to_response("status160/partials/connection_edit.html", {'contact':contact, 'form':form },context_instance=RequestContext(request))

@login_required
def view_connections(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    return render_to_response("status160/partials/connection_view.html", {'object':contact},context_instance=RequestContext(request))
