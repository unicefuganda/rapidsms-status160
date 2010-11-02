from django import template
from django.db.models import Q
from poll.models import Poll, Response
import datetime

def lastmessage(contact):
    try:
        poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
        return Reponse.objects.filter(message__connection__contact=contact, poll=poll).latest('message__date').eav.poll_text_value
    except:
        return ''
    

register = template.Library()
register.filter('lastmessage', lastmessage)