from generic.sorters import Sorter
from rapidsms.models import Connection
from poll.models import Poll, Response, Category, ResponseCategory
import datetime
from django.db.models import Q

class StatusSorter(Sorter):
    def sort(self, column, object_list, ascending=True):
        full_contact_list = list(object_list)
        toret = []
        unknown = []
        unclear = []
        safe = []
        unsafe = []
        category_dict = {
            'safe':safe,
            'unsafe':unsafe,
            'unclear':unclear,
            'unknown':unknown,
        }
        print "%d CONTACTS" % len(full_contact_list)
        polls = list(Poll.objects.filter(contacts__in=object_list).exclude(start_date=None).filter(Q(end_date=None) | (~Q(end_date=None) & Q(end_date__gt=datetime.datetime.now()))).distinct().order_by('-start_date'))
        print "%d POLLS" % len(polls)
        for p in polls:
            for r in p.responses.order_by('-date'):
                if not (r.contact in unknown or r.contact in unclear or r.contact in safe or r.contact in unsafe) and r.contact in object_list:
                    category = None
                    if r.categories.filter(is_override=True).count():
                        category = r.categories.filter(is_override=True)[0].category
                    elif r.categories.filter(category__name__in=['safe', 'unsafe']):
                        category = r.categories.filter(category__name__in=['safe','unsafe'])[0].category
                    elif r.categories.count():
                        category = r.categories.all()[0].category
                    if category:
                        category_dict[category.name].append(r.contact)
            noresponse = []
            for c in p.contacts.all():
                if not (c in (safe + unsafe + unclear + unknown)) and c in object_list:
                    noresponse.append(c)
            unknown = unknown + noresponse
            category_dict['unknown'] = unknown
        
        nopoll = []
        for c in full_contact_list:
            if not (c in (safe + unsafe + unclear + unknown)):
                nopoll.append(c)

        toret = unsafe + unknown + unclear + safe + nopoll
        if not ascending:
            toret.reverse()
        return toret