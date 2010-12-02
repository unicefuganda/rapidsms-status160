from django.conf import settings
from django import forms
from rapidsms.models import Contact, Connection, ConnectionBase
from .models import WardenRelationship, Team, Agency
from simple_locations.models import Area
from poll.models import Poll, ResponseCategory, Response
from status160.templatetags.status import status

class FilterContactForm(forms.Form): # pragma: no cover
    
    wardens = forms.ModelMultipleChoiceField(queryset=Contact.objects.filter(pk__in=WardenRelationship.objects.all().values_list('warden', flat=True)).order_by('name'), required=False)
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all().order_by('name'), required=False)
    agencies = forms.ModelMultipleChoiceField(queryset=Agency.objects.all().order_by('name'), required=False)
    locations = forms.ModelMultipleChoiceField(queryset=Area.objects.filter(kind__name='Office').order_by('name'), required=False)
    search_string = forms.CharField(max_length=1000, required=False)
    
class MassTextForm(forms.Form):
    text = forms.CharField(max_length=160, required=True)
    
class CreateEventForm(forms.Form):
    short_description = forms.CharField(max_length=32, required=True)
    text_question = forms.CharField(max_length=160, required=True)

class ContactsForm(forms.Form):
    contacts = forms.ModelMultipleChoiceField(queryset=Contact.objects.all(), widget=forms.CheckboxSelectMultiple())
    
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
            initial_category = status(contact, "status")
            if initial_category:
                initial_category = initial_category.category
            self.fields['status'] = forms.ModelChoiceField(required=True, queryset=poll.categories.all(), initial=initial_category) 

class ConnectionForm(forms.Form): # pragma: no cover
    identity = forms.IntegerField()
