from django.contrib import admin


from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    RecipeTag,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('favorite_count',)

    def favorite_count(self, obj):
        return obj.favorites.all().count()

    favorite_count.short_description = 'Число добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
