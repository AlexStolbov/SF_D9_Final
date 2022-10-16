from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required


@login_required
def add_to_authors(request):
    user = request.user
    authors_group_name = 'authors'
    if not request.user.groups.filter(name=authors_group_name).exists():
        authors_group = Group.objects.get(name=authors_group_name)
        authors_group.user_set.add(user)
    return redirect('/')
