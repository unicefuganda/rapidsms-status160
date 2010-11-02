from django import template
from django.db.models import Q
from poll.models import Poll, Response, ResponseCategory
import datetime

def status(contact, property):
    try:
        poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
        try:
            r = ResponseCategory.objects.filter(is_override=True, response__poll=poll, response__message__connection__contact=contact).latest('response__message__date')
        except ResponseCategory.DoesNotExist:
            try:    
                r = ResponseCategory.objects.filter(category__name__in=['safe','unsafe'], response__poll=poll, response__message__connection__contact=contact).latest('response__message__date')           
            except ResponseCategory.DoesNotExist:
                try:
                    r = ResponseCategory.objects.filter(response__poll=poll, response__message__connection__contact=contact).latest('response__message__date')
                except ResponseCategory.DoesNotExist:
                    r = None
        if property == 'color':
            if not r:
                return 'FF7'
            else:
                return r.category.color
        elif property == 'name':
            if not r:
                return 'unknown'
            else:
                return r.category.name
        elif property == 'number':
            if not r:
                return 2
            else: 
                return r.category.priority
        else:
            return r
    except Poll.DoesNotExist:
        if property == 'number':
            return 4
        else:
            return ''
    except:
        return None
    

register = template.Library()
register.filter('status', status)