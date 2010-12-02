from django.db.models import Q
from operator import itemgetter
from rapidsms.models import Contact, Connection
from .models import WardenRelationship, Team, Agency, Alert
from poll.models import Poll, Category
from django.contrib.sites.models import Site
from rapidsms_httprouter.router import get_router
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.models import Backend
from status160.templatetags.status import status

def create_status_survey(description, question, contacts, user):
    poll = Poll.create_yesno(
         description,
         question,
         '',
         contacts,
         user
    )
    poll.sites.add(Site.objects.get_current())
    yes_category = poll.categories.get(name='yes')
    yes_category.name = 'safe'
    yes_category.response = "We received your response as 'yes',please send any updates to the system if your situation changes or you have useful information to provide." 
    yes_category.priority = 4
    yes_category.color = '99ff77'
    yes_category.save()
    no_category = poll.categories.get(name='no')
    no_category.response = "We received your response as 'no',please send any updates to the system if your situation changes or you have useful information to provide."
    no_category.name = 'unsafe' 
    no_category.priority = 1
    no_category.color = 'ff9977'
    no_category.save()            
    unknown_category = poll.categories.get(name='unknown')
    unknown_category.default = False
    unknown_category.priority = 2
    unknown_category.color = 'ffff77'
    unknown_category.save()
    unclear_category = Category.objects.create(
        poll=poll,
        name='unclear',
        default=True,
        color='ffff77',
        response='We have recorded but did not understand your response,please repeat (with a yes or no response)',
        priority=3
    )
    poll.start()
    return poll

def send_mass_text(contacts, text):
    connections = Connection.objects.filter(contact__in=contacts).distinct()
    router = get_router()
    for conn in connections:
        outgoing = OutgoingMessage(conn, text)
        router.handle_outgoing(outgoing)

def send_alert():
    alert = Alert()
    alert.save()
    
    for warden in WardenRelationship.objects.all():
        outstanding = []
        for dependent in warden.dependents.all():
            status_num = status(dependent, 'number')
            if int(status_num) < 3:
                outstanding.append((dependent, status_num))
                
        if (len(outstanding)):
            outstanding = sorted(outstanding, key=itemgetter(1), reverse=True)
            smstext = "%s persons still unaccounted for/unsafe:" % str(len(outstanding))
            text = smstext
            toadd = ''
            off = 0
            while (len(text) < 476) and (off < len(outstanding)):
                smstext = text
                if outstanding[off][0].default_connection:
                    
                    text += "%s(%s)" % (outstanding[off][0].name, outstanding[off][0].default_connection.identity)
                else:
                    text +="%s" % outstanding[off][0].name
                if off < (len(outstanding) - 1):
                    text += ','
                off += 1
    
            if off == len(outstanding) and len(text) < 476:
                smstext = text
            if off < len(outstanding):
                smstext += '...'

            router = get_router()
            for conn in Connection.objects.filter(contact=warden.warden):
                outgoing = OutgoingMessage(conn, smstext)
                router.handle_outgoing(outgoing)    

def filter_contacts(wardens, teams, agencies, locations, search_string):
    contacts = Contact.objects.all()
    query = None
    if len(wardens):
        for warden in wardens:
            if query:
                query = query | Q(pk__in=WardenRelationship.objects.get(warden=warden).dependents.all()) 
            else:
                query = Q(pk__in=WardenRelationship.objects.get(warden=warden).dependents.all())
        contacts = contacts.filter(query)
    if len(teams):
        contacts = contacts.filter(groups__in=teams)
    if len(agencies):
        contacts = contacts.filter(groups__in=agencies)
    if len(locations):
        contacts = contacts.filter(reporting_location__in=locations)
    if search_string:
            pks = []
            # split terms if the "OR" operator is used
            terms = [term.strip() for term in search_string.lower().split(' or ')]        
            return contacts.filter(
                (reduce(
                    lambda x, y: x | y,
                    [(Q(name__icontains=term) |
                      Q(groups__name__icontains=term))
                     for term in terms]
                ))).distinct()

    return contacts

PREFIXES = [('70', 'warid'), ('75', 'zain'), ('71', 'utl'), ('', 'dmark')]

def assign_backend(number):
    if number.startswith('0'):
        number = '256' + number[1:]
    backendobj = None
    for prefix, backend in PREFIXES:
        if number[3:].startswith(prefix):
            backendobj, created = Backend.objects.get_or_create(name=backend)
            break
    return (number, backendobj)

