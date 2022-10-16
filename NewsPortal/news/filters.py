from django_filters import FilterSet, DateFilter, ModelMultipleChoiceFilter
from .models import Post, Category
from django import forms


class PostFilter(FilterSet):
    created = DateFilter(
        lookup_expr='gt',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    category = ModelMultipleChoiceFilter(
        # field_name='category__postcategory__category',  # можно короче запись сделать
        field_name='postcategory__category',  # связь
        queryset=Category.objects.all(),  # для отбора используем все материалы
        label='Category',  # заголовок поля
    )

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'author__user__username': ['icontains'],
        }
