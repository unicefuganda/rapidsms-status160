from django.db import models

from django.contrib.auth.models import Group

from poll.models import Poll

from rapidsms.models import Contact

class Comments(models.Model):
    """
    Blaster allows people to add comments to a user's status regarding
    a particular security event
    """
    event = models.ForeignKey(Poll, related_name='comments')
    user = models.ForeignKey(Contact)
    text = models.CharField(max_length=2000)
    
    def __unicode__(self):
        return self.text

class WardenRelationship(models.Model):
    """
    Wardens are responsible for managing a contact list and ensuring
    the people on it are safe.  This creates a tree structure (or
    calling tree) amongst the contact.
    """
    warden = models.ForeignKey(Contact, related_name="warden")
    dependents = models.ManyToManyField(Contact, related_name="charges")
    
    class Meta:
        permissions = (
            ("password_updated", "Password updated"),
        )
    
class Alert(models.Model):
    """
    This keeps a log of Alerts going out to Wardens, and when they've
    been sent (to avoid spamming)
    """
    sent = models.DateTimeField(auto_now_add=True)

class Team(Group):
    """
    In Status160, Reporters are allowed to have 0-n teams,
    but we still represent these within the list of groups.
    """
    pass

class Agency(Group):
    """
    In Status160, Reporters are allowed to only have 1 Agency,
    but this is enforced at the view level, not within the model,
    for convenience, as both teams and agencies act exactly like
    groups in all other respects.
    """
    pass

