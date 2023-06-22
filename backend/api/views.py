from urllib.parse import unquote

from rest_framework.viewsets import ReadOnlyModelViewSet

from api.models import Tag, Ingredient
from api.permissions import ReadOnly
from api.serializers import TagSerializer, IngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        search_name = self.request.GET.get('name')
        if search_name:
            decoded_name = unquote(search_name)
            queryset = queryset.filter(name__istartswith=decoded_name)
        return queryset
