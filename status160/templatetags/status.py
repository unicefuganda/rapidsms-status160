from django import template
from django.db.models import Q
from poll.models import Poll, Response, ResponseCategory
import datetime

def status(contact, property):
    try:
        poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
        response = None
        user_override_response = None
        try:
            user_override_response = ResponseCategory.objects.filter(is_override=True, response__poll=poll, response__contact=contact).latest('response__date')
        except ResponseCategory.DoesNotExist:
            pass
        last_clear_response = None
        try:
            last_clear_response = ResponseCategory.objects.filter(category__name__in=['safe','unsafe'], response__poll=poll, response__contact=contact).latest('response__date')           
        except ResponseCategory.DoesNotExist:
            try:
                last_clear_response = ResponseCategory.objects.filter(response__poll=poll, response__contact=contact).latest('response__date')
            except ResponseCategory.DoesNotExist:
                pass
        if last_clear_response and user_override_response:
            if last_clear_response.response.date < user_override_response.response.date:
                response = user_override_response
            else:
                response = last_clear_response
        elif last_clear_response:
            response = last_clear_response
        else:
            response = user_override_response
        if property == 'color':
            if not response:
                return 'FF7'
            else:
                return response.category.color
        elif property == 'name':
            if not response:
                return 'unknown'
            else:
                return response.category.name
        elif property == 'number':
            if not response:
                return 2
            else: 
                return response.category.priority
        else:
            return response
    except Poll.DoesNotExist:
        if property == 'number':
            return 4
        else:
            return ''
    except:
        return None
    

register = template.Library()
register.filter('status', status)