from rapidsms.models import Backend

#PREFIXES = [('70', 'warid'), ('75', 'zain'), ('71', 'utl'), ('', 'dmark')]

def assign_backend(number):
    if number.startswith('0'):
        number = '256%s' % number[1:]
    backendobj, _ = Backend.objects.get_or_create(name='yo8700')
#    for prefix, backend in PREFIXES:
#        if number[3:].startswith(prefix):
#            backendobj, created = Backend.objects.get_or_create(name=backend)
#            break
    return (number, backendobj)

