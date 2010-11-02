from django import template

def warden(contact):
    try:
        return contact.charges.all()[0].warden.name
    except:
        return None
    

register = template.Library()
register.filter('warden', warden)