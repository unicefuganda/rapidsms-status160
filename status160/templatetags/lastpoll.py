from django import template
from django.db.models import Q
from poll.models import Poll, Response
import datetime

def lastpoll(contact, property):
    try:
        poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
        return poll.__dict__[property]
    except:
        return None
    

register = template.Library()
register.filter('lastpoll', lastpoll)