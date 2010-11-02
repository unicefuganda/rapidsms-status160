from django import template
from django.db.models import Q
from poll.models import Poll
import datetime

def comments(contact):
    try:
        poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
        return poll.comments.filter(user=contact)
    except Poll.DoesNotExist:
        return None
    

register = template.Library()
register.filter('comments', comments)