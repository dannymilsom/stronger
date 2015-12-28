from django.db import models


class Group(models.Model):
    """
    Represents a group of users who want to share progress
    information.

    Group ID will be used to form URLs and should not
    contain spaces. The name is a user friendly screen label.
    """

    name = models.CharField(max_length=20, primary_key=True)
    about = models.CharField(max_length=500)
    created = models.DateField()
    background_url = models.URLField(
        default="http://uxrepo.com/static/icon-sets/elusive/svg/group.svg")

    def count_members(self):
        """Returns the number of members in a given group."""
        return self.get_members().count()

    def get_members(self):
        """Returns all user object members for a given group."""
        from . import GroupMember
        return GroupMember.objects.filter(group=self.name)

    def get_members_usernames(self):
        """Returns a list of all group member usernames."""
        return [m.user.username for m in self.get_members()]

    def get_pending_members(self):
        """Returns a QuerySet of members not yet approved by a group admin."""
        from . import GroupMember
        return GroupMember.objects.filter(group=self.group_id, approved=False)

    def get_admin(self):
        """Returns a QuerySet of members with admin permissions."""
        from . import GroupMember
        return GroupMember.objects.filter(group=self.group_id, admin=True)

    def get_admin_usernames(self):
        """Returns a list of group member usernames with admin permsissions."""
        return [a.user.username for a in self.get_admin()]

    def __unicode__(self):
        return self.name
