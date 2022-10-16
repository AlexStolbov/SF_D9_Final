from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import add_to_authors

urlpatterns = [
    path('', LogoutView.as_view(template_name='sign/logout.html'), name='logout'),
    path('add_to_authors/', add_to_authors, name='add_to_group_authors')
]
