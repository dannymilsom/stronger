from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from ..forms import GroupForm
from stronger.models import Group, GroupMember

@login_required
def group(request, group_name):
    """Details for a partiuclar group."""

    group = get_object_or_404(Group, name=group_name)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()

    data = {
        'group': group,
        'group_form': GroupForm(instance=group)
    }

    return render(request, "group.html", data)

@login_required
def groups(request):
    """Renders a page displaying information about all group instances."""

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            Group.objects.create(
                name=request.POST.get('name'),
                about=request.POST.get('about'),
                created=timezone.now().date()
            )

    memberships = GroupMember.objects.filter(user=request.user)
    groups = [mem.group for mem in memberships.select_related('group')]
    data = {
        'groups': groups,
        'group_form': GroupForm(),
    }

    return render(request, "groups.html", data)
