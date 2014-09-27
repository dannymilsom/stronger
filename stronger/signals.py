from django.conf import settings
from django.db.models import signals
from django.db import IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.utils.text import get_text_list

from rest_framework.authtoken.models import Token

from stronger.models import StrongerUser

@receiver(post_save, sender=StrongerUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Create a auth token for use with the REST API.
    """
    if created:
        Token.objects.create(user=instance)

def check_unique_together(sender, **kwargs):
    """
    Check models unique_together manually. Django enforced unique together 
    only the database level, but some databases (e.g. SQLite) don't
    support this.
    """

    instance = kwargs["instance"]
    for field_names in sender._meta.unique_together:
        model_kwargs = {}
        for field_name in field_names:
            try:
                data = getattr(instance, field_name)
            except FieldDoesNotExist:
                # e.g.: a missing field, which is however necessary.
                # The real exception on model creation should be raised. 
                continue
            model_kwargs[field_name] = data

        query_set = sender.objects.filter(**model_kwargs)
        if instance.pk != None:
            # Exclude the instance if it was saved in the past
            query_set = query_set.exclude(pk=instance.pk)

        count = query_set.count()
        if count > 0:
            field_names = get_text_list(field_names, _('and'))
            msg = _(u"%(model_name)s with this %(field_names)s already exists.") % {
                'model_name': unicode(instance.__class__.__name__),
                'field_names': unicode(field_names)
            }
            raise IntegrityError(msg)

def auto_add_check_unique_together(model_class):
    """
    Add only the signal handler check_unique_together, if a database 
    without UNIQUE support is used (e.g. SQLite in dev)
    """
    if settings.DATABASE_ENGINE in ('sqlite3',): # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        signals.pre_save.connect(check_unique_together, sender=model_class)

