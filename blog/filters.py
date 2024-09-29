import django_filters

from blog.models import Blog

class TagFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(field_name='tags__tag', lookup_expr='icontains')

    class Meta:
        model = Blog
        fields = ['tags']