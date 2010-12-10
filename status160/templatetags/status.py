from django import template
from django.db.models import Q
from poll.models import Poll, Response, ResponseCategory
import datetime

def status(contact, property=None):
    nosurvey_attr_dict = {
        'color':'',
        'name':'',
        'number':4,
    }
    try:
        poll = Poll.objects.filter(contacts=contact).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).latest('start_date')
        responsecategory = poll.categories.get(name='unknown')
        user_override_response = None
        last_clear_response = None
        try:
            user_override_response = ResponseCategory.objects.filter(is_override=True, response__poll=poll, response__contact=contact).latest('response__date')
        except ResponseCategory.DoesNotExist:
            pass
        try:
            last_clear_response = ResponseCategory.objects.filter(category__name__in=['safe','unsafe'], response__poll=poll, response__contact=contact).latest('response__date')           
        except ResponseCategory.DoesNotExist:
            try:
                last_clear_response = ResponseCategory.objects.filter(response__poll=poll, response__contact=contact).latest('response__date')
            except ResponseCategory.DoesNotExist:
                pass
        if last_clear_response is not None and user_override_response is not None:
            if last_clear_response.response.date < user_override_response.response.date:
                responsecategory = user_override_response.category
            else:
                responsecategory = last_clear_response.category
        elif last_clear_response is not None:
            responsecategory = last_clear_response.category
        elif user_override_response is not None:
            responsecategory = user_override_response.category
        if property:
            return responsecategory.__getattribute__(property)
        else:
            return responsecategory
    except Poll.DoesNotExist:
        if property:
            return nosurvey_attr_dict[property]
        else:
            return None
    

register = template.Library()
register.filter('status', status)