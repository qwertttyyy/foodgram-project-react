from django_filters import rest_framework as filters, BaseInFilter

from api.models import Recipe


class InFilter(BaseInFilter, filters.CharFilter):
    pass


class RecipeFilter(filters.FilterSet):
    tags = InFilter(
        field_name='tags__slug', lookup_expr='in', method='filter_tags'
    )
    author = filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()
