from datetime import datetime


class AuthorPreSaveMixin(object):
    """Set additional attributes which are implicit from the request."""

    def pre_save(self, obj):
        obj.added_by = self.request.user
        obj.added_at = datetime.now()
        super(AuthorPreSaveMixin, self).pre_save(self, obj)
